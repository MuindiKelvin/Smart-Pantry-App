document.addEventListener('DOMContentLoaded', function() {
    let dict = new Map();
    let count = 0;

    function initializeQuagga() {
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#interactive')
            },
            decoder: {
                readers: ["upc_reader", "ean_reader"]
            }
        }, function(err) {
            if (err) {
                console.error(err);
                return;
            }
            Quagga.start();
        });

        Quagga.onDetected(function(data) {
            if (dict.has(data.codeResult.code)) {
                dict.set(data.codeResult.code, dict.get(data.codeResult.code) + 1);
            } else {
                dict.set(data.codeResult.code, 1);
            }
            count += 1;

            if (count == 15) {
                let maxKey = null;
                let maxValue = 0;

                for (let [key, value] of dict) {
                    if (value > maxValue) {
                        maxValue = value;
                        maxKey = key;
                    }
                }

                fetch(`https://world.openfoodfacts.org/api/v0/product/${maxKey}.json`)
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.product) {
                            const productName = data.product.product_name_en;
                            const imageUrl = data.product.image_url;

                            document.getElementById('food_name').value = productName;

                            // Update image URL input and show thumbnail
                            document.getElementById('food_image_url').value = imageUrl;
                            var imagePreview = document.getElementById('imagePreview');
                            var fileInput = document.getElementById('food_image');
                            var imagePreviewContainer = document.getElementById('imagePreviewContainer');

                            imagePreview.src = imageUrl;
                            imagePreviewContainer.style.display = 'block';
                            fileInput.style.display = 'none';

                            stopQuagga();
                        } else {
                            console.log("Product data not found");
                            stopQuagga();
                        }
                    })
                    .catch(error => console.error('Error fetching data:', error));
            }
        });
    }

    function stopQuagga() {
        Quagga.stop();
        var modal = document.getElementById("cameraModal");
        modal.style.display = "none";
        count = 0;
        dict.clear();
    }

    document.getElementById('scanBarcodeButton').addEventListener('click', function() {
        var modal = document.getElementById("cameraModal");
        modal.style.display = "flex";
        initializeQuagga();
    });

    var modal = document.getElementById("cameraModal");
    window.onclick = function(event) {
        if (event.target == modal) {
            stopQuagga();
        }
    };
});






const inputs = document.querySelectorAll(".input-field");
const toggle_btn = document.querySelectorAll(".toggle");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");
const images = document.querySelectorAll(".image");


inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});

toggle_btn.forEach((btn) => {
  btn.addEventListener("click", () => {
    main.classList.toggle("sign-up-mode");
  });
});

let currentIndex = 0;

function moveSlider(event) {
  let index;

  if(event && this.dataset.value) {
    index = this.dataset.value;
    currentIndex = index;
  } else {
    currentIndex = (currentIndex % bullets.length) + 1;
    index = currentIndex;
  }

  let currentImage = document.querySelector(`.img-${index}`);
  images.forEach((img) => img.classList.remove("show"));
  currentImage.classList.add("show");

  const textSlider = document.querySelector(".text-group");
  textSlider.style.transform = `translateY(${-(index - 1) * 2.8}rem)`;

  bullets.forEach((bull) => bull.classList.remove("active"));
  document.querySelector(`[data-value='${index}']`).classList.add("active");
}


setInterval(moveSlider, 5000);

bullets.forEach((bullet) => {
  bullet.addEventListener("click", moveSlider);
});

// This function toggles the sign-up mode based on the URL hash
function handleHashChange() {
  if (window.location.hash === "#signup") {
      main.classList.add("sign-up-mode");
  } else if (window.location.hash === "#signin") {
      main.classList.remove("sign-up-mode");
  }
}

// Check the hash on page load and adjust UI accordingly
document.addEventListener("DOMContentLoaded", handleHashChange);

// Adjust UI when the URL hash changes
window.addEventListener("hashchange", handleHashChange);


// Confirm password validation
document.addEventListener('DOMContentLoaded', (event) => {
  // Check if the element exists
  var resetPasswordForm = document.getElementById("reset-password-form");
  
  // If it exists, then we attach the submit event listener
  if (resetPasswordForm) {
    resetPasswordForm.addEventListener("submit", function(event) {
      var password = document.getElementById("new-password").value;
      var confirmPassword = document.getElementById("confirm-password").value;

      if (password !== confirmPassword) {
          event.preventDefault();
          document.getElementById("errorMessage").textContent = "Passwords do not match!";
      } else {
          document.getElementById("errorMessage").textContent = "";
      }
    });
  }
});





// Index Page
//sidebar
const menuItems = document.querySelectorAll('.menu-item');
const messagesNotification = document.querySelector('#messages-notifications');
const messages = document.querySelector('.messages');
const message = messages.querySelectorAll('.message');
const messageSearch = document.querySelector('#message-search');

//remove active class from all menu items
const changeActiveItem = () => {
    menuItems.forEach(item => {
        item.classList.remove('active');
    })
}
 

menuItems.forEach(item => {
    item.addEventListener('click', () => {
        changeActiveItem();
        item.classList.add('active');
        
        if (item.id != 'notifications') {
            document.querySelector('.notifications-popup').style.display = 'none';
        } else {
            document.querySelector('.notifications-popup').style.display = 'block';
            document.querySelector('#notifications .notification-count').style.display='none';
        }
    })
})


const searchMessage = () => {
    const val = messageSearch.value.toLowerCase();
    message.forEach(chat => {
        let name=chat.querySelector('h5').textContent.toLowerCase();
        if(name.indexOf(val) != -1){
            chat.style.display = 'flex';
        } else{
            chat.style.display = 'none';
        }
    })
}

messageSearch.addEventListener('keyup', searchMessage);


messagesNotification.addEventListener('click', () => {
    messages.style.boxShadow = '0 0 1rem var(--color-primary)';
    messagesNotification.querySelector('.notification-count').style.display = 'none';
    setTimeout(() => {
        messages.style.boxShadow = 'none';
    }, 2000);
})



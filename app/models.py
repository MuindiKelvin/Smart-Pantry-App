from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, case, func, and_
from app import *
import os
from pathlib import Path
import requests
from werkzeug.utils import secure_filename
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from sqlalchemy import func

class User(db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # hashed value
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'], salt='mysalt')
        return s.dumps({'user_id': self.user_id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'], salt='mysalt')
        try:
            user_id = s.loads(token)['user_id']
            print(user_id)
        except:
            return None
        return User.query.get(user_id)

class FoodCategory(db.Model):
    __tablename__ = 'FoodCategories'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)


class FoodInventory(db.Model):
    __tablename__ = 'FoodInventory'
    
    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('FoodCategories.category_id'), nullable=False)
    food_name = db.Column(db.String(255), nullable=False)
    purchase_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    memo = db.Column(db.String(100))
    status = db.Column(db.String(20))

    @classmethod
    def create_new(cls, user_id, category_id, food_name, expiration_date, quantity, memo):
        new_food_item = cls(
            user_id=user_id,
            category_id=category_id,
            food_name=food_name,
            purchase_date=datetime.today(),
            expiration_date=expiration_date,
            quantity=quantity,
            memo=memo
        )
        db.session.add(new_food_item)
        db.session.commit()
        return new_food_item
    
    @classmethod
    def delete_with_images(cls, food_id):
        food_item = cls.query.get(food_id)
        if food_item:
            FoodImage.query.filter_by(food_id=food_id).delete()
            db.session.delete(food_item)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def check_and_notify_expiring_items(cls, threshold=7):
        threshold_date = (datetime.utcnow() + timedelta(days=threshold)).date()

        # Query food items nearing expiration
        expiring_items = cls.query.filter(
            cls.expiration_date == threshold_date
        ).all()

        for item in expiring_items:
            # Create notification content
            if threshold > 0:
                content = f"Reminder: '{item.food_name}' is expiring on {item.expiration_date.strftime('%Y-%m-%d')}. Consider consuming this item or sharing with your community."
            else:
                content = f"Reminder: '{item.food_name}' has expired on {item.expiration_date.strftime('%Y-%m-%d')}."

            # Create and add notification to the database
            notification = Notification(
                user_id=item.user_id,
                content=content,
                status='Unread'
            )
            db.session.add(notification)

        db.session.commit()
        return threshold_date

    @staticmethod
    def fetch_user_inventory(user_id):
        results = db.session.query(
            FoodInventory.food_name,
            FoodInventory.quantity,
            FoodCategory.category_name,
            FoodInventory.expiration_date,
            FoodInventory.memo
        ).join(
            FoodCategory, FoodInventory.category_id == FoodCategory.category_id
        ).filter(
            FoodInventory.user_id == user_id
        ).order_by(
        FoodInventory.expiration_date
        ).all()

        # Calculate status and days to expiry based on expiration date
        for result in results:
            expiry = result.expiration_date
            
            if expiry:
                days_left = 0 if (expiry - date.today()).days < 0 else (expiry - date.today()).days
                print(days_left)
                if days_left <= 0:
                    status = "Expired"
                    days_left = f"Expired {abs(days_left)} days ago"
                else:
                    days_left = f"{days_left} days left"
            else:
                days_left = "No Expiry Date"
                status = "Unknown"
            
            yield (result.food_name, result.quantity, result.category_name, days_left, status, result.memo)

    @staticmethod
    def fetch_user_inventory_for_category(user_id, category_id):
        current_date = func.current_date() 

        results = db.session.query(
            FoodInventory.food_id,
            FoodInventory.food_name,
            FoodInventory.quantity,
            FoodCategory.category_name,
            FoodInventory.expiration_date,
            FoodInventory.memo,
            FoodInventory.status,
            FoodImage.image_path
        ).join(
            FoodCategory, FoodInventory.category_id == FoodCategory.category_id
        ).outerjoin(
            FoodImage, FoodInventory.food_id == FoodImage.food_id
        ).filter(
            FoodInventory.user_id == user_id,
            FoodInventory.category_id == category_id
        ).order_by(
            case(
                (FoodInventory.expiration_date == None, 1),
                else_=0
            ),
            case(
                (FoodInventory.expiration_date >= func.current_date(), 0),
                (FoodInventory.expiration_date < func.current_date(), 1),
                else_=0
            ),
            FoodInventory.expiration_date
        ).all()

        # Calculate status and days to expiry based on expiration date
        for result in results:
            expiry = result.expiration_date

            if expiry:
                days_left = (expiry - date.today()).days
                if days_left <= 0:
                    status = "Expired"
                    days_left = f"Expired {abs(days_left)} days ago"
                else:
                    status = "Good"
                    days_left = f"{days_left} days left"
            elif expiry is None and result.status == "Consumed":
                days_left = "Consumed"
                status = "Consumed"
            else:
                days_left = "No Expiry Date"
                status = "Unknown"
            image_path = Path(result.image_path).as_posix() if result.image_path else None
            yield (result.food_name, result.quantity, result.category_name, days_left, status, result.memo, image_path, result.food_id, result.status)
    

    @classmethod
    def fetch_inventory_analytics(cls, user_id):
        current_date = func.current_date()

        # Count for available (not expired) food items
        available_count = db.session.query(func.count()).filter(
            cls.user_id == user_id,
            cls.expiration_date > current_date,
            cls.status == None
        ).scalar()

        # Count for expired food items
        expired_count = db.session.query(func.count()).filter(
            cls.user_id == user_id,
            cls.expiration_date <= current_date,
            cls.status == None
        ).scalar()

        # Count for consumed food items
        consumed_count = db.session.query(func.count()).filter(
            cls.user_id == user_id,
            cls.status == 'Consumed'
        ).scalar()

        return {
            'available': available_count,
            'expired': expired_count,
            'consumed': consumed_count
        }

    def mark_as_consumed(self):
        self.quantity = 0
        self.expiration_date = None  # Set to None instead of '0000-00-00' for compatibility
        self.memo = None
        self.status = "Consumed"
        db.session.commit()

    def mark_as_expired(self):
        self.quantity = 0
        self.expiration_date = date.today()-timedelta(days=1)
        self.memo = None
        self.status = "Expired"
        db.session.commit()



class SharedFood(db.Model):
    __tablename__ = 'SharedFood'
    
    share_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_id = db.Column(db.Integer, db.ForeignKey('FoodInventory.food_id'), nullable=False)
    sharing_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_for_sharing = db.Column(db.Date)
    status = db.Column(db.Enum('Available', 'Claimed', 'Shared'), nullable=False)
    title = db.Column(db.String(255), nullable=False) 
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer)

    @classmethod
    def create_new(cls, food_id, status, title, description,quantity):
        new_shared_food = cls(
            food_id=food_id,
            sharing_date=datetime.today(),
            status=status,
            title=title,
            description=description,
            quantity=quantity
        )
        db.session.add(new_shared_food)
        db.session.commit()
        return new_shared_food  

    @staticmethod
    def get_total_quantity_being_shared(food_id):
        result = db.session.query(func.sum(SharedFood.quantity)).filter(SharedFood.food_id == food_id).scalar()
        return result if result is not None else 0
    
    @staticmethod
    def get_user_shared_items(user_id):
        result = db.session.query(
            SharedFood.share_id,
            SharedFood.title,
            SharedFood.description,
            SharedFood.quantity,
            FoodInventory.food_name,
            FoodInventory.expiration_date,
            SharedFood.status
        ).join(FoodInventory, SharedFood.food_id == FoodInventory.food_id)\
         .filter(FoodInventory.user_id == user_id)\
         .all()
        yield from result
    
    
    @staticmethod
    def find_shared_food_by_zip_and_status(user_id, zip_code):
        results = db.session.query(
            SharedFood.share_id,
            SharedFood.food_id,
            FoodInventory.expiration_date,
            SharedFood.title,
            SharedFood.description,
            SharedFood.quantity,
            FoodInventory.user_id,
            (FoodInventory.user_id == user_id).label('posted_by_same_user'),
            db.case(
                (SharedFoodClaims.claimer_user_id == user_id, SharedFoodClaims.claim_id),
                else_=None
            ).label('user_claim_id'),
            FoodImage.image_path,
            User.email.label('sharer_email')
        ).join(
            FoodInventory, SharedFood.food_id == FoodInventory.food_id
        ).outerjoin(
            FoodImage, FoodInventory.food_id == FoodImage.food_id
        ).join(
            User, FoodInventory.user_id == User.user_id
        ).outerjoin(
            SharedFoodClaims, SharedFood.share_id == SharedFoodClaims.share_id
        ).filter(
            User.zip_code == zip_code,
            SharedFood.status == "Shared"
        ).group_by(
            SharedFood.share_id
        ).all()

        return [
            {
                'share_id': item[0],
                'food_id': item[1],
                'expiry_date': item[2],
                'title': item[3],
                'description': item[4],
                'quantity': item[5],
                'user_id': item[6],
                'posted_by_same_user': item[7],
                'user_claim_id': item[8],
                'food_image_path': item[9].replace('\\', '/') if item[9] is not None else 'img/food_images/noimagedefault.jpg',
                'sharer_email': None if item[8] is None else item[10],
                'email_subject': f'Inquiry About Your Smart Pantry Post: {item[3]}' if item[8] is not None else None
            }
            for item in results
        ]

class SharedFoodClaims(db.Model):
    __tablename__ = 'SharedFoodClaims'
    
    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    share_id = db.Column(db.Integer, db.ForeignKey('SharedFood.share_id'), nullable=False)
    claimer_user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    claim_date = db.Column(db.DateTime, default=datetime.utcnow)
    claimfoodstatus = db.Column(db.Integer, default=0)

    @classmethod
    def create_new_claim(cls, share_id, user_id):
        """Create and save a new food claim."""
        new_claim = cls(
            share_id=share_id,
            claimer_user_id=user_id,
            claim_date=datetime.utcnow(),
            claimfoodstatus=0
        )
        try:
            db.session.add(new_claim)
            db.session.commit()
            return new_claim
        except Exception as e:
            db.session.rollback()
            return None
        
    @staticmethod
    def get_claim_details_by_share_id(share_id):
        results = db.session.query(
            SharedFoodClaims.claimer_user_id,
            func.concat(User.first_name, " ", User.last_name).label('name'),
            SharedFoodClaims.claim_date,
            User.email,
            SharedFoodClaims.claimfoodstatus,
            SharedFoodClaims.claim_id
        ).join(User, User.user_id == SharedFoodClaims.claimer_user_id)\
        .filter(SharedFoodClaims.share_id == share_id)\
        .all()
        results = [
            {
                'claimer_user_id': row[0],
                'name': row[1],
                'claim_date': row[2].isoformat() if row[2] else None,
                'email': row[3],
                'claimfoodstatus': row[4],
                'claim_id': row[5]
            }
            for row in results
        ]

        return results
    
    @staticmethod
    def get_user_claims(user_id):
        claims = db.session.query(
            SharedFoodClaims.claim_id,
            SharedFood.title,
            FoodInventory.expiration_date,
            SharedFoodClaims.claimfoodstatus,
            SharedFood.status,
            User.email,
            SharedFood.description,
            SharedFood.quantity,
            SharedFoodClaims.claim_date
        ).join(SharedFood, SharedFoodClaims.share_id == SharedFood.share_id)\
        .join(FoodInventory, SharedFood.food_id == FoodInventory.food_id)\
        .join(User, FoodInventory.user_id == User.user_id)\
        .filter(SharedFoodClaims.claimer_user_id == user_id)\
        .all()

        claim_details_list = []

        for claim in claims:
            claim_details_list.append({
                'claim_id': claim[0],
                'title': claim[1],
                'expiration_date': claim[2].isoformat() if claim[2] else None,
                'claimfoodstatus': claim[3],
                'sharedfood_status': claim[4],
                'sharer_email': claim[5],
                'description': claim[6],
                'quantity': claim[7],
                'claim_date': claim[8].date().isoformat() if claim[8] else None,
                'email_subject': f'Inquiry About Your Smart Pantry Post: {claim[3]}'
            })

        return claim_details_list


class Notification(db.Model):
    __tablename__ = 'Notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Enum('Read', 'Unread'), nullable=False)

    @classmethod
    def get_notifications_for_user(cls, user_id):
        notifications = (
            cls.query
            .filter_by(user_id=user_id)
            .order_by(cls.notification_date.desc())
            .all()
        )

        result = [
            {
                "notification_id": notification.notification_id,
                "content": notification.content,
                "notification_date": notification.notification_date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": notification.status
            }
            for notification in notifications
        ]
        return result
    
    @classmethod
    def unread_count(cls, user_id):
        return cls.query.filter_by(user_id=user_id, status='Unread').count()


    def mark_as_read(self):
        self.status = 'Read'
        db.session.commit()
    
    def delete_notification(self):
        db.session.delete(self)
        db.session.commit()


class FoodImage(db.Model):
    __tablename__ = 'FoodImages'
    
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_id = db.Column(db.Integer, db.ForeignKey('FoodInventory.food_id'), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    @classmethod
    def save_image(cls, food_id, file=None, image_url=None, upload_folder=None):
        def download_image(url):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = secure_filename(url.split('/')[-1])
                image_path = os.path.join(upload_folder, 'food_images', filename)
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return os.path.join('img', 'food_images', filename)
            else:
                return None

        if file and cls.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_directory = os.path.join(upload_folder, 'food_images')
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)
            image_full_path = os.path.join(image_directory, filename)
            file.save(image_full_path)
            relative_image_path = os.path.join('img', 'food_images', filename)
        elif image_url:
            relative_image_path = download_image(image_url)
        else:
            return None

        if relative_image_path:
            new_food_image = cls(food_id=food_id, image_path=relative_image_path)
            db.session.add(new_food_image)
            db.session.commit()
            return new_food_image
            
    @staticmethod
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

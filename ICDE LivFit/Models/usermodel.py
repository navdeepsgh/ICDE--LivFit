from flask import session
from Models.databasemodel import Database
import datetime
from datetime import date
from passlib.hash import sha256_crypt

class Customer(object):

    def __init__(self, name, age, gender, height, weight, occupation, email, password, aim, date, bookings, exercise_log, user_type='customer', _id=None):
        self.name=name
        self.age=age
        self.gender=gender
        self.height=height
        self.weight=weight
        self.occupation=occupation
        self.email=email
        self.password=password
        self.aim=aim
        self.date=date
        self.bookings=bookings
        self.exercise_log=exercise_log
        self.user_type='customer'
        self._id= None
        
    
    @classmethod
    def get_by_email_login(cls, user_type, email):
        data = Database.find_one("users", {"email":email})
        if data is not None and data['user_type']==user_type:
            return cls(**data)
    
    @classmethod
    def get_by_email_signup(cls, email):
        data = Database.find_one("users", {"email":email})
        if data is not None:
            return False
        else:
            return True
    
    @classmethod
    def get_customer(cls, email):
        data = Database.find_one("users", {"email":email})
        return cls(**data)
    
    @staticmethod
    def login_valid(user_type, email, password):
        user= Customer.get_by_email_login(user_type, email)
        if user is not None:
            return sha256_crypt.verify(password, user.password)
        return False
    
    @classmethod
    def signup(cls, name, age, gender, height, weight, occupation, email, password, aim, date):
        user = Customer.get_by_email_signup(email)
        if user:
            bookings = []
            exercise_log = []
            new_user = cls(name, age, gender, height, weight, occupation, email, password, aim, date, bookings, exercise_log)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email
    
    @staticmethod
    def logout():
        session['email'] = None
    
    def json(self):
        return {
            'name' : self.name,
            'age' : self.age,
            'gender' : self.gender,
            'height' : self.height,
            'weight' : self.weight,
            'occupation' : self.occupation,
            'email' : self.email,
            'password' : self.password,
            'aim' : self.aim,
            'date' : self.date,
            'bookings':self.bookings,
            'exercise_log':self.exercise_log,
            'user_type' : self.user_type
        }
    
    def save_to_mongo(self):
        Database.insert("users", self.json())


class CustomerWeight(Customer):
    @staticmethod
    def update_weight(weight_details, email):
        current_user=CustomerWeight.get_customer(email)
        current_user.weight.append(weight_details)
        Database.update_user("users", {"email":current_user.email}, {"$set":{"weight":current_user.weight}})


class ExerciseLog(Customer):
    @staticmethod
    def update_exercise_log(exercise_details, email):
        current_user=ExerciseLog.get_customer(email)
        current_user.exercise_log.append(exercise_details)
        Database.update_user("users", {"email":current_user.email}, {"$set":{"exercise_log":current_user.exercise_log}})


class CustomerBookings(Customer):
    @staticmethod
    def update_bookings(booking_details, email):
        current_user=CustomerBookings.get_customer(email)
        if current_user.bookings == []:
            current_user.bookings.append(booking_details)
            Database.update_user("users", {"email":current_user.email}, {"$set":{"bookings":current_user.bookings}})
        elif current_user.bookings[len(current_user.bookings)-1]['status'] == 'Trainer Alloted':
            current_user.bookings.append(booking_details)
            Database.update_user("users", {"email":current_user.email}, {"$set":{"bookings":current_user.bookings}})
        else:
            current_user.bookings.pop()
            current_user.bookings.append(booking_details)
            Database.update_user("users", {"email":current_user.email}, {"$set":{"bookings":current_user.bookings}})


class Trainer(object):

    def __init__(self, name, age, gender, experience, email, password, date, bookings, user_type='trainer', _id=None):
        self.name=name
        self.age=age
        self.gender=gender
        self.experience=experience
        self.email=email
        self.password=password
        self.date=date
        self.bookings=bookings
        self.user_type='trainer'
        self._id= None
    
    @classmethod
    def get_by_email_login(cls, user_type, email):
        # for displaying correct profile page on login
        data = Database.find_one("users", {"email":email})
        if data is not None and data['user_type']==user_type:
            return cls(**data)
    
    @classmethod
    def get_by_email_signup(cls, email):
        data = Database.find_one("users", {"email":email})
        print(data)
        if data is not None:
            return False
        else:
            return True
    
    @classmethod
    def get_trainer(cls, email):
        data = Database.find_one("users", {"email":email})
        return cls(**data)
    
    @staticmethod
    def login_valid(user_type, email, password):
        user= Trainer.get_by_email_login(user_type, email)
        if user is not None:
            return user.password == password
        return False
    
    @classmethod
    def signup(cls, name, age, gender, experience, email, password, date):
        user = Trainer.get_by_email_signup(email)
        if user:
            bookings=[]
            new_user = cls(name, age, gender, experience, email, password, date, bookings)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False
    
    @staticmethod
    def login(user_email):
        session['email'] = user_email
    
    @staticmethod
    def logout():
        session['email'] = None
    
    def json(self):
        return {
            'name' : self.name,
            'age' : self.age,
            'gender' : self.gender,
            'experience' : self.experience,
            'email' : self.email,
            'password' : self.password,
            'date' : self.date,
            'bookings':self.bookings,
            'user_type' : self.user_type
        }
    
    def save_to_mongo(self):
        Database.insert("users", self.json())


class TrainerBookings(Trainer):
    @staticmethod
    def update_bookings(booking_details, name):
        data = Database.find_one("users", {"name":name})
        email = data['email']
        current_user=TrainerBookings.get_trainer(email)
        current_user.bookings.append(booking_details)
        Database.update_user("users", {"email":current_user.email}, {"$set":{"bookings":current_user.bookings}})


class CustomerAssistance(Customer):

    @staticmethod
    def customer_average(email):
        customer = CustomerAssistance.get_customer(email)
        i=0
        total_time = 0
        for exercise in customer.exercise_log:
            total_time = total_time + int(exercise['total time'])
            i=i+1
        if i!=0:
            average_time = total_time/i
        else:
            average_time=0
        return average_time
    
    @staticmethod
    def overall_average(email):
        customer = CustomerAssistance.get_customer(email)
        data = Database.find("users", {'aim': customer.aim})
        i=0
        total_time=0
        for user in data:
            if user['exercise_log'] != []:
                for exercise in user['exercise_log']:
                    total_time = total_time + int(exercise['total time'])
                    i=i+1
        if i!=0:
            overall_average = total_time/i
        else:
            overall_average=0
        return overall_average
    
    @staticmethod
    def popular_exercises(email):
        weightloss_exercises = {'Forward Lunge': 0,
                    'Burpee': 0,
                    'Explosive Lunge': 0,
                    'Squat': 0,
                    'Double Jump': 0}
        
        musclegain_exercises = {'Running': 0,
                                'Push-ups': 0,
                                'Crunches': 0,
                                'Dips': 0,
                                'Plank': 0}
        customer = CustomerAssistance.get_customer(email)
        data = Database.find("users", {'aim': customer.aim})

        if customer.aim == 'weightloss':
            for user in data:
                for exercise in user['exercise_log']:
                    weightloss_exercises[exercise['exercise_1']] = weightloss_exercises[exercise['exercise_1']] + 1
                    weightloss_exercises[exercise['exercise_2']] = weightloss_exercises[exercise['exercise_2']] + 1
            popular = []
            popular.insert(0, 'Forward Lunge')
            for item in weightloss_exercises:
                if weightloss_exercises[item] > weightloss_exercises[popular[0]]:
                    popular.pop()
                    popular.insert(0, item)
            for item in weightloss_exercises:
                if len(popular) == 1:
                    if item != popular[0]:
                        popular.insert(1, item)
                    else:
                        continue
                elif weightloss_exercises[item] > weightloss_exercises[popular[1]] and item != popular[0]:
                    popular.pop()
                    popular.insert(1, item)
                else:
                    continue
            return popular

        else:
            for user in data:
                for exercise in user['exercise_log']:
                    musclegain_exercises[exercise['exercise_1']] = musclegain_exercises[exercise['exercise_1']] + 1
                    musclegain_exercises[exercise['exercise_2']] = musclegain_exercises[exercise['exercise_2']] + 1
            
            popular = []
            popular.insert(0, 'Running')
            for item in musclegain_exercises:
                if musclegain_exercises[item] > musclegain_exercises[popular[0]]:
                    popular.pop()
                    popular.insert(0, item)
            for item in musclegain_exercises:
                if len(popular) == 1:
                    if item != popular[0]:
                        popular.insert(1, item)
                    else:
                        continue
                elif musclegain_exercises[item] > musclegain_exercises[popular[1]] and item != popular[0]:
                    popular.pop()
                    popular.insert(1, item)
                else:
                    continue
            return popular
    
    @staticmethod
    def loss_journey(email):
        customer = CustomerAssistance.get_customer(email)
        if customer.aim == 'weightloss':
            progress =[]
            if len(customer.weight) == 1:
                data = customer.weight.pop()
                val = (float(data[0]), 0)
                progress.append(val)
                return progress
            else:
                data = customer.weight[0]
                val = (data[0], 0)
                progress.append(val)
                for i in range(len(customer.weight)-1):
                    if i == 0:
                        weight_one = customer.weight[i]
                        weight_two = customer.weight[i+1]
                        date_data_one = weight_one[1].split("-")
                        date_data_two = weight_two[1].split("-")
                        date_one = date(int(date_data_one[0]), int(date_data_one[1]), int(date_data_one[2]))
                        date_two = date(int(date_data_two[0]), int(date_data_two[1]), int(date_data_two[2]))
                        days = (date_two-date_one).days
                        val = (weight_two[0], days)
                        progress.append(val)
                    else:
                        weight_one = customer.weight[0]
                        weight_two = customer.weight[i+1]
                        date_data_one = weight_one[1].split("-")
                        date_data_two = weight_two[1].split("-")
                        date_one = date(int(date_data_one[0]), int(date_data_one[1]), int(date_data_one[2]))
                        date_two = date(int(date_data_two[0]), int(date_data_two[1]), int(date_data_two[2]))
                        days = (date_two-date_one).days
                        val = (weight_two[0], days)
                        progress.append(val)
                return progress

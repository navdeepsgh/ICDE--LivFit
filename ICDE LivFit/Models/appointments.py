from Models.databasemodel import Database
import datetime


class Appointment(object):

    def __init__(self, pending, _id='appointments'):
        self.pending = pending
        self._id=_id
    

    @classmethod
    def check_existence(cls,idd):
        data= Database.find_one("appointments", {"_id": idd})
        if data is not None:
            return cls(**data)
        else:
            return None
    
    @classmethod
    def create(cls):
        pending=[]
        new = cls(pending)
        new.save_to_mongo()
    
    @classmethod
    def book_appointment(cls, name, email):
        unique_id = f'{email}-{datetime.datetime.today().strftime("%Y-%m-%d")}'
        check='appointments'
        appointment_booking = Appointment.check_existence(check)
        if appointment_booking is not None:
            booking_details = {"id": unique_id,
                                "status":"Request Received",
                                "customer_name":name,
                                "customer_email":email,
                                "trainer_name":" "}
            appointment_booking.pending.append(booking_details)
            Database.update_user("appointments", {"_id":appointment_booking._id}, {"$set":{"pending":appointment_booking.pending}})
            return booking_details
        else:
            Appointment.create()
            appointment_booking=Appointment.check_existence(check)
            booking_details = {"id": unique_id,
                                "status":"Request Received",
                                "customer_name":name,
                                "customer_email":email,
                                "trainer_name":" "}
            appointment_booking.pending.append(booking_details)
            Database.update_user("appointments", {"_id":appointment_booking._id}, {"$set":{"pending":appointment_booking.pending}})
            return booking_details

    @classmethod
    def total_requests(cls):
        check='appointments'
        data=Appointment.check_existence(check)
        return len(data.pending)
    
    @classmethod
    def update_requests(cls, details):
        data=Appointment.check_existence('appointments')
        data.pending=details
        Database.update_user("appointments", {"_id":data._id}, {"$set":{"pending":data.pending}})

    def json(self):
        return {
            '_id' : self._id,
            'pending' : self.pending
        }
    
    def save_to_mongo(self):
        Database.insert("appointments", self.json())
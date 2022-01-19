from flask import Flask, render_template, redirect, request, url_for, session, flash
from Models.usermodel import Customer, Trainer, CustomerWeight, ExerciseLog, CustomerBookings, TrainerBookings, CustomerAssistance
from Models.databasemodel import Database
import datetime
from Models.appointments import Appointment
from passlib.hash import sha256_crypt


fapp = Flask(__name__)
fapp.secret_key='navdeep'


@fapp.route('/')
def home_page():
    return render_template('home.html')


@fapp.route('/customersignup/')
def customer_signup_page():
    return render_template('finalcustomersignup.html')


@fapp.route('/trainersignup/')
def trainer_signup_page():
    return render_template('finaltrainersignup.html')


@fapp.route('/login/')
def login_page():
    session['email']=None
    return render_template('login.html')


@fapp.before_first_request
def initialize_database():
    Database.initialize()


@fapp.route('/auth/login', methods=['POST'])
def login_user():
    if request.method=='GET':
        session['email']=None
        return redirect(url_for('login_page'))
    else:
        session['email'] = None
        email = request.form['email']
        password = request.form['password']
        user_type=request.form['type']
        
        if user_type=='customer' and Customer.login_valid(user_type, email, password):
            Customer.login(email)
            return redirect(url_for('customer_profile'))
        elif user_type=='trainer' and Trainer.login_valid(user_type, email, password):
            Trainer.login(email)
            return  redirect(url_for('trainer_profile'))
        else:
            session['email'] = None
            flash("Invalid Login Credentials", "error")
        return  redirect(url_for('login_page'))


@fapp.route('/auth/customersignup', methods=['POST'])
def customer_registration():
    session['email'] = None
    name=request.form['name']
    age=request.form['age']
    gender=request.form['gender']
    height=request.form['height']
    weight=[(request.form['weight'], datetime.datetime.today().strftime("%Y-%m-%d"))]
    occupation=request.form['occupation']
    email=request.form['email']
    password=sha256_crypt.encrypt(request.form['password'])
    aim=request.form['aim']
    date=datetime.datetime.today().strftime("%Y-%m-%d")

    if Customer.signup(name, age, gender, height, weight, occupation, email, password, aim, date):
        return  render_template('customerprofile.html', email=session['email'])
    else:
        flash("User Already Exist, Kindly Login", "error")
        return redirect(url_for('customer_signup_page'))


# customer profile page
@fapp.route('/customerprofile/')
def customer_profile():
    if session['email'] == None:
        return redirect(url_for('login_page'))
    
    else:
        return render_template('customerprofile.html', email=session['email'])   


# trainer profile page
@fapp.route('/trainerprofile/')
def trainer_profile():
    if session['email'] == None:
        return redirect(url_for('login_page'))
    else:
        return render_template('trainerprofile.html', email=session['email'])


@fapp.route('/auth/trainersignup', methods=['POST'])
def trainer_registration():
    session['email'] = None
    name=request.form['name']
    age=request.form['age']
    gender=request.form['gender']
    experience=request.form['experience']
    email=request.form['email']
    password=sha256_crypt.encrypt(request.form['password'])
    date=datetime.datetime.today().strftime("%Y-%m-%d")

    if Trainer.signup(name, age, gender, experience, email, password, date):
        return render_template('trainerprofile.html', email=session['email'])
    else:
        flash("User Already Exist, Kindly Login", "error")
        return redirect(url_for('trainer_signup_page'))


# to logout irrespective of customer or trainer
@fapp.route('/logout/')
def logout():
    session['email'] = None
    return redirect(url_for('home_page'))


#displaying customer profile details
@fapp.route('/customerprofiledetails/', methods=['GET','POST'])
def customer_profile_details():

    if request.method == 'POST':
        updated_weight = (request.form['updatedweight'], datetime.datetime.today().strftime("%Y-%m-%d"))
        CustomerWeight.update_weight(updated_weight, session['email'])
        return redirect(url_for('customer_profile_details'))
    else:
        current_customer = Customer.get_customer(session['email'])
        print(current_customer.weight)
        return render_template('customerprofiledetails.html', name=current_customer.name, age=current_customer.age,
                                gender=current_customer.gender, height=current_customer.height, weight=current_customer.weight,
                                occupation=current_customer.occupation, email=current_customer.email, aim=current_customer.aim, date= current_customer.date)


#displaying trainer profile details
@fapp.route('/trainerprofiledetails/')
def trainer_profile_details():
    current_trainer = Trainer.get_trainer(session['email'])
    return render_template('trainerprofiledetails.html', name=current_trainer.name, age=current_trainer.age,
                            gender=current_trainer.gender, experience= current_trainer.experience, email=current_trainer.email, date=current_trainer.date)


# view exercise
@fapp.route('/viewexercises/')
def view_exercises():
    current_customer=Customer.get_customer(session['email'])

    if current_customer.aim == 'weightloss':
        return render_template('weightloss2.html')
    else:
        return render_template('musclegain2.html')


@fapp.route('/bookappointment/')
def get_appointment():
    current_customer=CustomerBookings.get_customer(session['email'])
    if current_customer.bookings == []:
        booking = Appointment.book_appointment(current_customer.name, session['email'])
        current_customer.update_bookings(booking, session['email'])
        return redirect(url_for('see_bookings'))
    elif current_customer.bookings[len(current_customer.bookings)-1]['status'] != 'Request Received':
        booking = Appointment.book_appointment(current_customer.name, session['email'])
        current_customer.update_bookings(booking, session['email'])
        return redirect(url_for('see_bookings'))
    else:
        flash("You already have one pending appointment request", "error")
        return redirect(url_for('customer_profile'))


@fapp.route('/viewcustomerbookings/')
def see_bookings():
    current_customer=CustomerBookings.get_customer(session['email'])
    bookings=current_customer.bookings
    return render_template('viewcustomerbookings.html', bookings=bookings)


@fapp.route('/confirmappointments/', methods=['GET','POST'])
def confirm_appointments():
    if request.method == 'GET':
        total_requests=Appointment.total_requests()
        return render_template('confirmappointments.html', total_requests=total_requests)
    else:
        requests=int(request.form['requests_taken'])
        current_trainer=TrainerBookings.get_trainer(session['email'])
        appointment_requests=Appointment.check_existence('appointments')
        for i in range(requests):
            data=appointment_requests.pending.pop(0)
            data['status']='Trainer Alloted'
            data['trainer_name']=current_trainer.name
            CustomerBookings.update_bookings(data, data['customer_email'])
            TrainerBookings.update_bookings(data, data['trainer_name'])
        Appointment.update_requests(appointment_requests.pending)
        flash(f'You have been alloted {requests} appointment requests. Please check details under View Bookings Option.','error')
        return redirect(url_for('trainer_profile'))


@fapp.route('/viewtrainerbookings/')
def see_trainer_bookings():
    current_trainer=TrainerBookings.get_trainer(session['email'])
    bookings=current_trainer.bookings
    return render_template('viewtrainerbookings.html', bookings=bookings)


@fapp.route('/exerciselog/', methods=['GET','POST'])
def enter_exercise_details():
    if request.method == 'POST':
        exercise_1 = request.form['exercise1']
        exercise_2 = request.form['exercise2']
        time = request.form['time']
        if exercise_1 == exercise_2:
            flash('Both exercises should be different','error')
            return redirect(url_for('enter_exercise_details'))
        else:
            current_customer=ExerciseLog.get_customer(session['email'])
            if current_customer.exercise_log != []:
                if current_customer.exercise_log[len(current_customer.exercise_log)-1]['date'] != datetime.datetime.today().strftime("%Y-%m-%d"):
                    exercise_details = {'exercise_1': exercise_1,
                                            'exercise_2':exercise_2,
                                            'total time':time,
                                            'date':datetime.datetime.today().strftime("%Y-%m-%d")}
                    current_customer.update_exercise_log(exercise_details, session['email'])
                    return redirect(url_for('enter_exercise_details'))
                else:
                    flash("You have already submitted today's exercise details",'error')
                    return redirect(url_for('enter_exercise_details'))
            else:
                exercise_details = {'exercise_1': exercise_1,
                                            'exercise_2':exercise_2,
                                            'total time':time,
                                            'date':datetime.datetime.today().strftime("%Y-%m-%d")}
                current_customer.update_exercise_log(exercise_details, session['email'])
                return redirect(url_for('enter_exercise_details'))
    else:
        current_customer=ExerciseLog.get_customer(session['email'])
        if current_customer.aim == 'weightloss':
            return render_template('recordexerciseswl.html', exercise_log = current_customer.exercise_log)
        else:
            return render_template('recordexercisesmg.html', exercise_log= current_customer.exercise_log)


@fapp.route('/customerassistance/')
def customer_assistance():
    customer_avg = CustomerAssistance.customer_average(session['email'])
    total_avg = CustomerAssistance.overall_average(session['email'])
    exercises = CustomerAssistance.popular_exercises(session['email'])
    customer = CustomerAssistance.get_customer(session['email'])
    if customer.aim == 'weightloss':
        progress = CustomerAssistance.loss_journey(session['email'])
        x=[]
        y=[]
        for p in progress:
            a,b = p
            x.append(b)
            y.append(a)
        return render_template('customerassistancewl.html', customer_avg=round(customer_avg, 2), total_avg=round(total_avg, 2), popular=exercises, labels=x, values=y)
    else:
        return render_template('customerassistancemg.html', customer_avg=customer_avg, total_avg=total_avg, popular=exercises)


if __name__=="__main__":
    fapp.run(debug=True)
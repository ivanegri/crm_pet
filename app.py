from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Tutor, Pet, Appointment, Product, Sale
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm_pet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    # Dashboard data
    today = datetime.now().date()
    appointments_today = Appointment.query.filter(db.func.date(Appointment.date_time) == today).all()
    recent_sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    return render_template("index.html", appointments=appointments_today, sales=recent_sales)


@app.route("/reports")
def reports():
    # Total Sales
    total_sales = db.session.query(db.func.sum(Sale.total)).scalar() or 0
    
    # Sales by Product
    sales_by_product = db.session.query(
        Product.name, db.func.sum(Sale.quantity), db.func.sum(Sale.total)
    ).join(Sale).group_by(Product.name).all()
    
    # Appointments by Service
    appts_by_service = db.session.query(
        Appointment.service, db.func.count(Appointment.id)
    ).group_by(Appointment.service).all()
    
    # Monthly Stats (Current Month)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    sales_this_month = db.session.query(db.func.sum(Sale.total)).filter(
        db.extract('month', Sale.date) == current_month,
        db.extract('year', Sale.date) == current_year
    ).scalar() or 0
    
    appts_this_month = db.session.query(db.func.count(Appointment.id)).filter(
        db.extract('month', Appointment.date_time) == current_month,
        db.extract('year', Appointment.date_time) == current_year
    ).scalar() or 0

    return render_template("reports.html", 
                           total_sales=total_sales,
                           sales_by_product=sales_by_product,
                           appts_by_service=appts_by_service,
                           sales_this_month=sales_this_month,
                           appts_this_month=appts_this_month)

# --- API / Action Routes ---

@app.route("/tutors", methods=["GET", "POST"])
def tutors():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        new_tutor = Tutor(name=name, phone=phone, address=address)
        db.session.add(new_tutor)
        db.session.commit()
        return redirect(url_for("tutors"))
    
    search = request.args.get("search")
    query = Tutor.query
    if search:
        query = query.filter(Tutor.name.ilike(f"%{search}%"))
    
    all_tutors = query.all()
    return render_template("tutors.html", tutors=all_tutors)

@app.route("/pets", methods=["GET", "POST"])
def pets():
    if request.method == "POST":
        name = request.form.get("name")
        breed = request.form.get("breed")
        age = request.form.get("age")
        tutor_id = request.form.get("tutor_id")
        new_pet = Pet(name=name, breed=breed, age=age, tutor_id=tutor_id)
        db.session.add(new_pet)
        db.session.commit()
        return redirect(url_for("pets"))

    search = request.args.get("search")
    query = Pet.query
    if search:
        query = query.join(Tutor).filter(
            (Pet.name.ilike(f"%{search}%")) | 
            (Tutor.name.ilike(f"%{search}%"))
        )

    all_pets = query.all()
    tutors = Tutor.query.all()
    return render_template("pets.html", pets=all_pets, tutors=tutors)

@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        service = request.form.get("service")
        date_str = request.form.get("date_time") # Expecting 'YYYY-MM-DDTHH:MM'
        date_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        
        new_appt = Appointment(pet_id=pet_id, service=service, date_time=date_time)
        db.session.add(new_appt)
        db.session.commit()
        return redirect(url_for("appointments"))

    search = request.args.get("search")
    query = Appointment.query.order_by(Appointment.date_time)
    if search:
        query = query.join(Pet).join(Tutor).filter(
            (Pet.name.ilike(f"%{search}%")) |
            (Tutor.name.ilike(f"%{search}%")) |
            (Appointment.service.ilike(f"%{search}%"))
        )

    all_appts = query.all()
    pets = Pet.query.all()
    return render_template("appointments.html", appointments=all_appts, pets=pets)

@app.route("/sales", methods=["GET", "POST"])
def sales():
    if request.method == "POST":
        product_name = request.form.get("product_name")
        price = float(request.form.get("price"))
        tutor_id = request.form.get("tutor_id")
        
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            product = Product(name=product_name, price=price)
            db.session.add(product)
            db.session.commit()
            
        new_sale = Sale(product_id=product.id, tutor_id=tutor_id if tutor_id else None, total=price)
        db.session.add(new_sale)
        db.session.commit()
        return redirect(url_for("sales"))

    search = request.args.get("search")
    query = Sale.query.order_by(Sale.date.desc())
    if search:
        query = query.join(Product).outerjoin(Tutor).filter(
            (Product.name.ilike(f"%{search}%")) |
            (Tutor.name.ilike(f"%{search}%"))
        )

    all_sales = query.all()
    tutors = Tutor.query.all()
    return render_template("sales.html", sales=all_sales, tutors=tutors)

# --- Edit & Delete Routes ---

@app.route("/tutor/edit/<int:id>", methods=["GET", "POST"])
def edit_tutor(id):
    tutor = db.session.get(Tutor, id)
    if not tutor:
        return redirect(url_for("tutors"))
    
    if request.method == "POST":
        tutor.name = request.form.get("name")
        tutor.phone = request.form.get("phone")
        tutor.address = request.form.get("address")
        db.session.commit()
        return redirect(url_for("tutors"))
    
    return render_template("edit_tutor.html", tutor=tutor)

@app.route("/tutor/delete/<int:id>")
def delete_tutor(id):
    tutor = db.session.get(Tutor, id)
    if tutor:
        # Optional: Handle associated pets/sales logic here if needed
        db.session.delete(tutor)
        db.session.commit()
    return redirect(url_for("tutors"))

@app.route("/pet/edit/<int:id>", methods=["GET", "POST"])
def edit_pet(id):
    pet = db.session.get(Pet, id)
    if not pet:
        return redirect(url_for("pets"))
    
    if request.method == "POST":
        pet.name = request.form.get("name")
        pet.breed = request.form.get("breed")
        pet.age = request.form.get("age")
        pet.tutor_id = request.form.get("tutor_id")
        db.session.commit()
        return redirect(url_for("pets"))
    
    tutors = Tutor.query.all()
    return render_template("edit_pet.html", pet=pet, tutors=tutors)

@app.route("/pet/delete/<int:id>")
def delete_pet(id):
    pet = db.session.get(Pet, id)
    if pet:
        db.session.delete(pet)
        db.session.commit()
    return redirect(url_for("pets"))

@app.route("/appointment/edit/<int:id>", methods=["GET", "POST"])
def edit_appointment(id):
    appt = db.session.get(Appointment, id)
    if not appt:
        return redirect(url_for("appointments"))
    
    if request.method == "POST":
        appt.pet_id = request.form.get("pet_id")
        appt.service = request.form.get("service")
        appt.status = request.form.get("status")
        date_str = request.form.get("date_time")
        appt.date_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        
        db.session.commit()
        return redirect(url_for("appointments"))
    
    pets = Pet.query.all()
    return render_template("edit_appointment.html", appt=appt, pets=pets)

@app.route("/appointment/delete/<int:id>")
def delete_appointment(id):
    appt = db.session.get(Appointment, id)
    if appt:
        db.session.delete(appt)
        db.session.commit()
    return redirect(url_for("appointments"))

@app.route("/sale/edit/<int:id>", methods=["GET", "POST"])
def edit_sale(id):
    sale = db.session.get(Sale, id)
    if not sale:
        return redirect(url_for("sales"))
    
    if request.method == "POST":
        # For simplicity, we allow editing price and tutor, but maybe not product name easily without changing product logic
        # Let's allow editing the total price and the tutor.
        sale.total = float(request.form.get("price"))
        sale.tutor_id = request.form.get("tutor_id")
        
        # If we want to change the product name, we'd need to update the Product model or link to a different product.
        # For this MVP, let's assume we just update the sale details.
        
        db.session.commit()
        return redirect(url_for("sales"))
    
    tutors = Tutor.query.all()
    return render_template("edit_sale.html", sale=sale, tutors=tutors)

@app.route("/sale/delete/<int:id>")
def delete_sale(id):
    sale = db.session.get(Sale, id)
    if sale:
        db.session.delete(sale)
        db.session.commit()
    return redirect(url_for("sales"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)

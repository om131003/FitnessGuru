from unittest import result

from flask import Flask, request,render_template,session,redirect,url_for,jsonify

from flask_session import Session
from werkzeug.utils import secure_filename
import pymysql
import os
import razorpay

import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
client = razorpay.Client(auth=("rzp_test_SawmDSCZDf6iCT", "ex7shOt5aHlaHtAwY0LNZNxG"))




conn = pymysql . connect(host='localhost',user='root',password='',database='db_gym')

UPLOAD_FOLDER ='static/dietcat_image/'
UPLOAD_FOLDER1 ='static/product_img'
UPLOAD_FOLDER2 ='static/exercise_video'
UPLOAD_FOLDER3 ='static/diet_image'
UPLOAD_FOLDER4='static/execat_image'


@app.route("/dashboard")
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    cursor= conn.cursor()

    # total Exercise Categories
    cursor.execute("SELECT COUNT(*) FROM tbl_exercisecategory")
    total_exercise_categories = cursor.fetchone()[0]

    #Total Exercises
    cursor.execute("SELECT COUNT(*)FROM tbl_manageexercise")
    total_exercises = cursor.fetchone()[0]

    # total Diet Categories
    cursor.execute("SELECT COUNT(*) FROM tbl_dietcategory")
    total_diet_categories = cursor.fetchone()[0]

    #Total Diet Plans
    cursor.execute("SELECT COUNT(*) FROM tbl_dietplans")
    total_diet_plans = cursor.fetchone()[0]

    #total products 
    cursor.execute("SELECT COUNT(*)FROM table_product")
    total_products = cursor.fetchone()[0]

    # --- ADD NEW MEMBERSHIPS LOGIC --
    query = """
        SELECT r.u_name, m.mp_planname, s.created_date, s.expired_date
        FROM tbl_sub s
        JOIN tbl_u_registration r ON s.u_id = r.u_id
        JOIN tbl_membershipplans m ON s.membership_id = m.membership_id
        ORDER BY s.created_date DESC
    """
    cursor.execute(query)
    memberships_db = cursor.fetchall()
    
    # Process the data to calculate status
    memberships = []
    current_date = datetime.now().date()
    for m in memberships_db:
        uname = m[0]
        plan = m[1]
        
        # safely handle datetime objects versus string dates
        purchase = m[2].date() if isinstance(m[2], datetime) else m[2]
        
        # Check if python needs to parse missing datatypes directly
        expiry = m[3] if m[3] else current_date
        if isinstance(expiry, datetime):
            expiry = expiry.date()
            
        status = "Active"
        try:
            if expiry < current_date:
                status = "Expired"
            elif (expiry - current_date).days <= 5:
                status = "Expiring Soon"
        except Exception:
            pass # fallback if type error on parsing dates
            
        memberships.append({
            'user_name': uname,
            'plan_name': plan,
            'purchase_date': purchase,
            'expiry_date': expiry,
            'status': status
        })

    return render_template("admin/dashboard.html"
                           , total_exercise_categories=total_exercise_categories
                           , total_exercises=total_exercises
                           , total_diet_categories=total_diet_categories
                           , total_diet_plans=total_diet_plans
                           , total_products=total_products
                           , memberships=memberships)

    




                  # exercise category
@app.route("/execat")
def execat():
    return render_template("admin/execat.html")

                   
@app.route("/add_execat", methods=["POST"])
def add_execat():
    cursor = conn.cursor()
    cat_name = request.form['cat_name']
    cat_image= request.files['cat_image']
    filename = secure_filename(cat_image.filename)
    cat_image.save(os.path.join(UPLOAD_FOLDER4,filename))
    path= os.path.join(UPLOAD_FOLDER4,filename)
    cat_desc =request.form['exercise_description']

    query = "INSERT INTO tbl_exercisecategory(cat_name,cat_image,exercise_description)VALUES(%s,%s,%s)"
    val = (cat_name,path,cat_desc)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('dashboard'))


@app.route("/view_execat")
def view_execat():
     cursor = conn.cursor()
     query = "SELECT * FROM tbl_exercisecategory"
     cursor.execute(query)
     view_execat = cursor.fetchall()
     return render_template("admin/view_execat.html",view_execat=view_execat)

     
@app.route('/delete_execat/<int:cat_id>')
def delete_execat(cat_id):
    cursor = conn.cursor()
    query = "DELETE FROM tbl_exercisecategory WHERE cat_id=%s"
    val=(cat_id)
    cursor.execute(query,val)
    conn.commit()
    return redirect(url_for('view_execat'))

@app.route("/edit_execat/<int:cat_id>")
def edit_execat(cat_id):
    cursor = conn.cursor()

    query = "SELECT * FROM tbl_exercisecategory WHERE cat_id=%s"
    val = (cat_id,)   

    cursor.execute(query, val)
    execat = cursor.fetchone()   

    cursor.close()

    return render_template("admin/edit_execat.html", edit_execat=execat)  # Γ£à name match

@app.route("/update_execat/<int:cat_id>", methods=["POST"])
def update_execat(cat_id):
    cursor = conn.cursor()
    cat_name = request.form['cat_name']
    cat_image = request.files['cat_image']
    filename = secure_filename(cat_image.filename)
    cat_image.save(os.path.join(UPLOAD_FOLDER4,filename))
    path= os.path.join(UPLOAD_FOLDER4,filename)
    cat_desc =request.form['exercise_description']
    query = "UPDATE tbl_exercisecategory SET cat_name=%s,cat_image=%s, exercise_description=%s WHERE cat_id=%s"
    val = (cat_name,path, cat_desc, cat_id)
    cursor.execute(query, val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_execat'))


                # diet category

@app.route("/adddietcat")
def adddietcat():
    return render_template("admin/adddietcat.html")

@app.route("/add_dietcat",methods=["POST"])
def add_dietcat():
    cursor = conn.cursor()
    dc_name = request.form['dc_name']
    dc_image =request.files['dc_image']
    filename = secure_filename(dc_image.filename)
    dc_image.save(os.path.join(UPLOAD_FOLDER,filename))
    path= os.path.join(UPLOAD_FOLDER,filename)

    query = "INSERT INTO tbl_dietcategory(dc_name,dc_image)VALUES(%s,%s)"
    val = (dc_name,path)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('dashboard'))

@app.route("/view_dietcat")
def view_dietcat():
     cursor = conn.cursor()
     query = "SELECT * FROM tbl_dietcategory"
     cursor.execute(query)
     view_dietcat = cursor.fetchall()
     return render_template("admin/view_dietcat.html",view_dietcat=view_dietcat)        

@app.route('/delete_dietcat/<int:dietcat_id>')
def delete_dietcat(dietcat_id):
    cursor = conn.cursor()
    query = "DELETE FROM tbl_dietcategory WHERE dietcat_id=%s"
    val=(dietcat_id)
    cursor.execute(query,val)
    conn.commit()
    return redirect(url_for('view_dietcat'))

@app.route("/edit_dietcat/<int:dietcat_id>")
def edit_dietcat(dietcat_id):       
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_dietcategory WHERE dietcat_id=%s"
    val=(dietcat_id)
    cursor.execute(query,val)
    edit_dietcat = cursor.fetchone()
    return render_template("admin/edit_dietcat.html",edit_dietcat=edit_dietcat)

@app.route("/update_dietcat/<int:dietcat_id>", methods=["POST"])
def update_dietcat(dietcat_id):
    cursor = conn.cursor()
    dc_name = request.form['dc_name']
    dc_image =request.files['dc_image']
    filename = secure_filename(dc_image.filename)
    dc_image.save(os.path.join(UPLOAD_FOLDER,filename))
    path= os.path.join(UPLOAD_FOLDER,filename)

    query = "UPDATE tbl_dietcategory SET dc_name=%s, dc_image=%s WHERE dietcat_id=%s"
    val = (dc_name,path, dietcat_id)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('view_dietcat'))



    



                            
                            
                            
                            # product 


@app.route("/productinventory")
def productinventory():
    return render_template("admin/productinventory.html")

@app.route("/add_product",methods=["POST"])
def add_product():
    cursor = conn.cursor()
    p_name = request.form['p_name']
    p_quantityinstock = request.form['p_quantityinstock']
    p_unitprice = request.form['p_unitprice']
    p_image =request.files['p_image']
    p_description = request.form['p_description']

    
    filename = secure_filename(p_image.filename)
    p_image.save(os.path.join(UPLOAD_FOLDER1,filename))
    path= os.path.join(UPLOAD_FOLDER1,filename)

    query = "INSERT INTO table_product(p_name,p_quantityinstock,p_unitprice,p_image,p_description)VALUES(%s,%s,%s,%s,%s)"
    val = (p_name,p_quantityinstock,p_unitprice,path,p_description)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('dashboard'))


@app.route("/view_product")
def view_product():
     cursor = conn.cursor()
     query = "SELECT * FROM table_product"
     cursor.execute(query)
     view_product = cursor.fetchall()
     return render_template("admin/view_product.html",view_product=view_product)

     
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id ):
    cursor = conn.cursor()
    query = "DELETE FROM table_product WHERE product_id=%s"
    val=(product_id )
    cursor.execute(query,val)
    conn.commit()
    return redirect(url_for('view_product'))

@app.route("/edit_product/<int:product_id>")
def edit_product(product_id):   
    cursor = conn.cursor()
    query = "SELECT * FROM table_product WHERE product_id=%s"
    val=(product_id)
    cursor.execute(query,val)
    view_product = cursor.fetchall()
    return render_template("admin/edit_product.html",view_product=view_product)

@app.route("/update_product", methods=["POST"])
def update_product():
    cursor = conn.cursor()
    product_id = request.form['product_id']
    p_name = request.form['p_name']
    p_quantityinstock = request.form['p_quantityinstock']
    p_unitprice = request.form['p_unitprice']
    p_image =request.files['p_image']
    p_description = request.form['p_description']
    filename = secure_filename(p_image.filename)
    p_image.save(os.path.join(UPLOAD_FOLDER1,filename))
    path= os.path.join(UPLOAD_FOLDER1,filename)
    query = "UPDATE table_product SET p_name=%s, p_quantityinstock=%s, p_unitprice=%s, p_image=%s, p_description=%s WHERE product_id=%s"
    val = (p_name,p_quantityinstock,p_unitprice,path,p_description, product_id)
    cursor.execute(query,val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_product'))






 
                                # ecercise

@app.route("/exercise")
def exercise():
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_exercisecategory"
    cursor.execute(query)
    view_execat = cursor.fetchall()
    return render_template("admin/exercise.html", view_execat=view_execat)

@app.route("/manageexe", methods=["POST"])
def manageexe():
    cursor = conn.cursor()

    exercise_name = request.form['exercise_name']
    cat_id = request.form['cat_id']
    video_url = request.files['video_url']
    exe_equipment = request.form['exe_equipment']
    exe_sets = request.form['exe_sets']
    exe_reps = request.form['exe_reps']
    exe_description = request.form['exe_description']

    exercise_video = secure_filename(video_url.filename)
    video_url.save(os.path.join(UPLOAD_FOLDER2, exercise_video))
    path = os.path.join(UPLOAD_FOLDER2, exercise_video)

    query = """
    INSERT INTO tbl_manageexercise
    (cat_id, exercise_name, video_url, exe_equipment, exe_sets, exe_reps, exe_description)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    val = (cat_id, exercise_name, path, exe_equipment, exe_sets, exe_reps, exe_description)

    cursor.execute(query, val)

    conn.commit()
    cursor.close()

    return redirect(url_for('dashboard'))

@app.route("/view_exercise")
def view_exercise():
        cursor = conn.cursor()
        query = """
        SELECT exercise_id, cat_name, exercise_name, video_url, exe_equipment, exe_sets, exe_reps,exe_description FROM tbl_manageexercise JOIN tbl_exercisecategory ON tbl_manageexercise.cat_id = tbl_exercisecategory.cat_id
        """
        cursor.execute(query)
        view_exercise = cursor.fetchall()
        return render_template("admin/view_exercise.html",view_exercise=view_exercise)

@app.route('/delete_exercise/<int:exercise_id>')
def delete_exercise(exercise_id):             
    cursor = conn.cursor()
    query = "DELETE FROM tbl_manageexercise WHERE exercise_id=%s"
    val=(exercise_id)
    cursor.execute(query,val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_exercise'))

@app.route("/edit_exercise/<int:exercise_id>")
def edit_exercise(exercise_id): 
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_exercisecategory"
    
    cursor.execute(query)
    viewcat= cursor.fetchall() 

    query1 = "SELECT * FROM tbl_manageexercise WHERE exercise_id=%s"
    val=(exercise_id)
    cursor.execute(query1,val)           
    view_exercise = cursor.fetchall()  
    
    cursor.close()
    return render_template("admin/edit_exercise.html",view_exercise=view_exercise,viewcat=viewcat)

@app.route("/update_exercise", methods=["POST"])
def update_exercise():
    cursor = conn.cursor()
    exercise_id = request.form['exercise_id']
    exercise_name = request.form['exercise_name']
    video_url =request.files['video_url']
    exe_equipment =request.form['exe_equipment']
    exe_sets =request.form['exe_sets']
    exe_reps =request.form['exe_reps']
    exe_description = request.form['exe_description']
    exercise_video = secure_filename(video_url.filename)
    video_url.save(os.path.join(UPLOAD_FOLDER2,exercise_video))
    path= os.path.join(UPLOAD_FOLDER2,exercise_video)
    query = "UPDATE tbl_manageexercise SET exercise_name=%s, video_url=%s, exe_equipment=%s, exe_sets=%s, exe_reps=%s, exe_description=%s WHERE exercise_id=%s"
    val = (exercise_name,path, exe_equipment, exe_sets, exe_reps, exe_description, exercise_id)
    cursor.execute(query, val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_exercise'))
    



                    # Membership plan


@app.route("/membershipplan")
def membershipplan():
    return render_template("admin/membershipplan.html")

@app.route("/add_member", methods=["POST"])
def add_member():
    cursor = conn.cursor()
    mp_planname = request.form['mp_planname']
    mp_durationmonths =request.form['mp_durationmonths']
    mp_price =request.form['mp_price']
    mp_status =request.form['mp_status']
    mp_benefits =request.form['mp_benefits']
    query = "INSERT INTO tbl_membershipplans(mp_planname,mp_durationmonths,mp_price,mp_status,mp_benefits)VALUES(%s,%s,%s,%s,%s)"
    val = (mp_planname,mp_durationmonths,mp_price,mp_status,mp_benefits)
    cursor.execute(query,val)
    conn.commit()
    cursor.close()
    return redirect(url_for('dashboard')) 

@app.route("/view_membership")
def view_membership():
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_membershipplans"
    cursor.execute(query)
    view_membership = cursor.fetchall()
    return render_template("admin/view_membership.html", view_membership=view_membership)

@app.route('/delete_membership/<int:membership_id>')
def delete_membership(membership_id):
    cursor = conn.cursor()
    query = "DELETE FROM tbl_membershipplans WHERE membership_id=%s"
    val =(membership_id)
    cursor.execute(query,val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_membership'))

@app.route("/edit_membership/<int:membership_id>")
def edit_membership(membership_id):
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_membershipplans WHERE membership_id=%s"
    val = (membership_id)
    cursor.execute(query, val)
    view_membership = cursor.fetchall()
    cursor.close()
    return render_template("admin/edit_membership.html", view_membership=view_membership)


@app.route("/update_membership", methods=["POST"])
def update_membership():
    cursor = conn.cursor()
    membership_id = request.form['membership_id']
    mp_planname = request.form['mp_planname']
    mp_durationmonths = request.form['mp_durationmonths']
    mp_price = request.form['mp_price']
    mp_benefits = request.form['mp_benefits']
    mp_status = request.form['mp_status']
    query = "UPDATE tbl_membershipplans SET mp_planname=%s, mp_durationmonths=%s, mp_price=%s, mp_status=%s, mp_benefits=%s WHERE membership_id=%s"
    val = (mp_planname, mp_durationmonths,mp_price, mp_status, mp_benefits, membership_id)
    cursor.execute(query, val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_membership'))







                        # diet plan
@app.route("/dietplans")
def dietplans():
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_dietcategory"
    cursor.execute(query)
    view_dietplans = cursor.fetchall()
    return render_template("admin/dietplans.html", view_dietplans=view_dietplans)

@app.route("/add_dietplans", methods=["POST"])
def add_dietplans():
    cursor = conn.cursor()
    dietcat_id=request.form['dietcat_id']
    dp_recipename = request.form['dp_recipename']
    dp_mealtype =request.form['dp_mealtype']
    dp_diettype =request.form['dp_diettype']
    dp_image =request.files['dp_image']
    dp_description = request.form['dp_description']

    filename = secure_filename(dp_image.filename)
    dp_image.save(os.path.join(UPLOAD_FOLDER3,filename))
    path= os.path.join(UPLOAD_FOLDER3,filename)

    query = "INSERT INTO tbl_dietplans(dietcat_id,dp_recipename,dp_mealtype,dp_diettype,dp_image,dp_description)VALUES(%s,%s,%s,%s,%s,%s)"
    val = (dietcat_id,dp_recipename,dp_mealtype,dp_diettype,path,dp_description)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('dashboard'))


@app.route("/view_dietplans")
def view_dietplans():
     cursor = conn.cursor()
     query = "SELECT a.dc_name,b.* FROM tbl_dietcategory as a,tbl_dietplans as b WHERE a.dietcat_id =b.dietcat_id"
     cursor.execute(query)
     view_dietplans = cursor.fetchall()
     return render_template("admin/view_dietplans.html",view_dietplans=view_dietplans)

     
@app.route('/delete_dietplan/<int:diet_id>')
def delete_dietplan(diet_id):
    cursor = conn.cursor()
    query = "DELETE FROM tbl_dietplans WHERE diet_id=%s"
    val=(diet_id )
    cursor.execute(query,val)
    conn.commit()
    return redirect(url_for('view_dietplans'))


@app.route("/edit_dietplan/<int:diet_id>")
def edit_dietplan(diet_id):
    cursor =conn.cursor()
    qurey = "SELECT * FROM tbl_dietcategory"
    cursor.execute(qurey)
    view_dietcat = cursor.fetchall()

    qurey1 = "SELECT * FROM tbl_dietplans WHERE diet_id=%s"
    val=(diet_id)
    cursor.execute(qurey1,val)
    view_dietplan = cursor.fetchall()
    cursor.close()  
    return render_template("admin/edit_dietplan.html", view_dietcat=view_dietcat, view_dietplan=view_dietplan)

@app.route("/update_dietplan", methods=["POST"])
def update_dietplan():           
    cursor = conn.cursor()
    diet_id = request.form['diet_id']
    dietcat_id=request.form['dietcat_id']  
    dp_recipename = request.form['dp_recipename']
    dp_mealtype =request.form['dp_mealtype']
    dp_diettype =request.form['dp_diettype']
    dp_image =request.files['dp_image']
    dp_description = request.form['dp_description']
    filename = secure_filename(dp_image.filename)
    dp_image.save(os.path.join(UPLOAD_FOLDER3,filename))
    path= os.path.join(UPLOAD_FOLDER3,filename)
    query = "UPDATE tbl_dietplans SET dietcat_id=%s, dp_recipename=%s, dp_mealtype=%s, dp_diettype=%s, dp_image=%s, dp_description=%s WHERE diet_id=%s"
    val = (dietcat_id, dp_recipename, dp_mealtype, dp_diettype, path, dp_description, diet_id)
    cursor.execute(query, val)
    conn.commit()
    cursor.close()
    return redirect(url_for('view_dietplans'))











                        # steps

@app.route("/steps")
def steps():
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_dietplans"
    cursor.execute(query)
    view_dietplans = cursor.fetchall()
    return render_template("admin/steps.html", view_dietplans=view_dietplans)



@app.route("/add_steps", methods=["POST"])
def add_steps():
    cursor = conn.cursor()

    recipe_name = request.form['recipe_name']
    st_description = request.form['st_description']
    st_ingredients = request.form['st_ingredients']   

    query = "INSERT INTO table_recipesteps(diet_id,st_description,st_ingredients) VALUES (%s,%s,%s)"
    val = (recipe_name, st_description, st_ingredients)

    cursor.execute(query, val)
    conn.commit()
    cursor.close()

    return redirect(url_for('dashboard'))



@app.route("/view_resteps")
def view_resteps():
     cursor = conn.cursor()
     query = "SELECT a.dp_recipename,b.* FROM tbl_dietplans as a,table_recipesteps as b WHERE a.diet_id=b.diet_id"
     cursor.execute(query)
     view_resteps = cursor.fetchall()
     return render_template("admin/view_resteps.html",view_resteps=view_resteps)
   
@app.route('/delete_resteps/<int:steps_id>')
def delete_resteps(steps_id):
    cursor = conn.cursor()
    query = "DELETE FROM table_recipesteps WHERE steps_id =%s"
    val=(steps_id)
    cursor.execute(query,val)
    conn.commit()
    return redirect(url_for('view_resteps'))


@app.route("/edit_steps/<int:steps_id>")
def edit_steps(steps_id):
    cursor = conn.cursor()
    qurey = "SELECT * FROM tbl_dietplans"
    cursor.execute(qurey)
    view_dietplans = cursor.fetchall()


    query1 = "SELECT * FROM table_recipesteps WHERE steps_id=%s"
    val =(steps_id)
    cursor.execute(query1,val)
    view_resteps = cursor.fetchall()
    cursor.close()
    return render_template("admin/edit_steps.html", view_dietplans=view_dietplans, view_resteps=view_resteps)



@app.route("/update_steps", methods=["POST"])
def update_steps():
    cursor = conn.cursor()

    steps_id = request.form['steps_id']
    diet_id = request.form['diet_id']
    st_description = request.form['st_description']
    st_ingredients = request.form['st_ingredients']   

    query = "UPDATE table_recipesteps SET diet_id=%s, st_description=%s, st_ingredients=%s WHERE steps_id=%s"
    val = (diet_id, st_description, st_ingredients, steps_id)

    cursor.execute(query, val)
    conn.commit()
    cursor.close()

    return redirect(url_for('view_resteps'))    

    





                # Login
@app.route("/")
def login():
    return render_template("admin/login.html")


@app.route("/adminloginprocess",methods=["POST"])
def adminloginprocess():
    cursor = conn.cursor()
    a_email = request.form['a_email']
    a_password = request.form['a_password']

    query = "SELECT * FROM tbl_admin WHERE a_email = %s AND a_password = %s"
    val = (a_email,a_password)
    cursor.execute(query,val)
    account = cursor.fetchone()

    if account:
        session['admin_id'] = account[0]
        session['a_email'] = account[1]

        msg ='logged in successfully !'
        # return render_template('/admin/dashboard.html', msg=msg)
        return redirect(url_for('dashboard'))
    else:
        msg ='incorrect username / password'
        return render_template('/admin/login.html', msg=msg)

@app.route("/viewcategory")
def viewcategory():
    return render_template("admin/viewcategory.html")


                        # logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))




                    #<================== USER SITE===================>




#<===================USER DASHBOARD==================>
# @app.route("/u_dashboard")
# def u_dashboard():
#     u_id = session.get('u_id')   # ✅ safe access

#     has_subscription = False  # default

#     if u_id:  # only check if logged in
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM tbl_sub WHERE u_id = %s", (u_id,))
#         result = cursor.fetchone()
#         has_subscription = result[0] > 0

#     return render_template("user/u_dashboard.html", has_subscription=has_subscription)


@app.route("/u_dashboard")
def u_dashboard():
    u_id = session.get('u_id')

    has_active_subscription = False
    is_expired = False
    membership_details = None

    if u_id:
        cursor = conn.cursor()

        query = """
            SELECT s.expired_date, m.mp_planname, s.amount 
            FROM tbl_sub s
            JOIN tbl_membershipplans m ON s.membership_id = m.membership_id
            WHERE s.u_id = %s 
            ORDER BY s.expired_date DESC 
            LIMIT 1
        """
        cursor.execute(query, (u_id,))
        result = cursor.fetchone()

        if result:
            expired_date = result[0]
            plan_name = result[1]
            amount_paid = result[2]
            current_date = datetime.now().date()

            if expired_date >= current_date:
                has_active_subscription = True
                status = "Active"
            else:
                is_expired = True
                status = "Expired"
                
            membership_details = {
                "plan_name": plan_name,
                "amount_paid": amount_paid,
                "expired_date": expired_date.strftime('%d %b, %Y') if expired_date else '',
                "status": status
            }

    return render_template(
        "user/u_dashboard.html",
        has_active_subscription=has_active_subscription,
        is_expired=is_expired,
        membership_details=membership_details
    )
# <===================USER REGISTRATION==================>
@app.route("/u_registration")
def u_registration():
    return render_template("user/u_registration.html")

@app.route("/u_registrationprocess", methods=["POST"])
def u_registrationprocess():
    cursor = conn.cursor()
    u_name = request.form['u_name']
    u_phone = request.form['u_phone']
    u_email = request.form['u_email']
    u_password = request.form['u_password']
    u_address = request.form['u_address']

    query = "INSERT INTO tbl_u_registration(u_name,u_phone,u_email,u_password,u_address)VALUES(%s,%s,%s,%s,%s)"
    val = (u_name,u_phone,u_email,u_password,u_address)
    cursor.execute(query,val)

    conn.commit()
    cursor.close()
    return redirect(url_for('u_login'))

@app.route("/u_login")
def u_login():
    return render_template("user/u_login.html")

@app.route("/u_loginprocess", methods=["POST"])
def u_loginprocess():

    cursor = conn.cursor()

    u_email = request.form.get('u_email')
    u_password = request.form.get('u_password')

    query = "SELECT * FROM tbl_u_registration WHERE u_email=%s AND u_password=%s"
    val = (u_email, u_password)

    cursor.execute(query, val)
    account = cursor.fetchone()

    if account:
        session['u_id'] = account[0]
        session['u_email'] = account[3]
        session['u_name'] = account[1]
        return redirect(url_for('u_dashboard'))
    else:
        msg = "Incorrect username / password"
        return render_template("user/u_login.html", msg=msg)
    

    # <===================USER LOGOUT==================>
@app.route("/u_logout")
def u_logout():
    session.pop('u_id', None)
    session.pop('u_email', None)
    return redirect(url_for('u_login')) 


# <===================CONTECT US==================>
@app.route("/u_contact")
def u_contact():
    return render_template("user/u_contact.html")


@app.route("/u_contactprocess", methods=["POST"])
def u_contactprocess():
    cursor = conn.cursor()

    c_name = request.form.get('c_name')
    c_email = request.form.get('c_email')
    c_message = request.form.get('c_message')

    query = "INSERT INTO tbl_u_contact (c_name, c_email, c_message) VALUES (%s, %s, %s)"
    values = (c_name, c_email, c_message)

    cursor.execute(query, values)
    conn.commit()

    cursor.close()

    return redirect(url_for('u_contact'))    


# <===================USER SHOPPING==================>
@app.route("/u_shopping")
def u_shopping():
    cursor = conn.cursor()
    query = "SELECT * FROM table_product"
    cursor.execute(query)
    data=cursor.fetchall() 
    return render_template("user/u_shopping.html",data=data)

@app.route("/u_productinfo/<int:product_id>")
def u_productinfo(product_id):
    cursor = conn.cursor()
    query = "SELECT * FROM table_product WHERE product_id=%s"
    val=(product_id,)
    cursor.execute(query,val)
    data = cursor.fetchall()
    return render_template("user/u_productinfo.html",data=data)


# <===================USER EXERCISE==================>
@app.route("/u_exercise")
def u_exercise():
    cursor=conn.cursor()
    query = "select * from tbl_exercisecategory"
    cursor.execute(query)
    data=cursor.fetchall()
    return render_template("user/u_exercise.html",data=data)



@app.route("/u_catexercise/<int:cat_id>")
def u_catexercise(cat_id):
    cursor=conn.cursor()
    query="select * from tbl_manageexercise where cat_id=%s"
    cursor.execute(query, (cat_id,))
    data=cursor.fetchall()
    return render_template("user/u_catexercise.html", data=data)


@app.route("/u_backdetails/<int:exercise_id>")
def u_backdetails(exercise_id):
    cursor=conn.cursor()
    query="select * from tbl_manageexercise where exercise_id=%s"
    cursor.execute(query, (exercise_id,))
    data=cursor.fetchall()
    return render_template("user/u_backdetails.html", data=data)

@app.route("/u_diet")
def u_diet():
    cursor=conn.cursor()
    query = "select * from tbl_dietcategory"
    cursor.execute(query)
    data=cursor.fetchall()
    return render_template("user/u_diet.html",data=data)



@app.route("/u_dietplans/<int:dietcat_id>")
def u_dietplans(dietcat_id):
    cursor=conn.cursor()
    query="select * from tbl_dietplans where dietcat_id=%s"
    cursor.execute(query, (dietcat_id ,))
    data=cursor.fetchall()
    return render_template("user/u_dietplans.html",data1=data)

@app.route("/u_dietdetails/<int:diet_id>")
def u_dietdetails(diet_id ):
    cursor=conn.cursor()
    query="select * from tbl_dietplans where diet_id =%s"
    cursor.execute(query, (diet_id ,))
    data=cursor.fetchall()
    return render_template("user/u_dietdetails.html",data=data)

@app.route("/u_recieps")
def u_recieps():
    cursor=conn.cursor()
    query = "select t.diet_id, d.dp_recipename from table_recipesteps t join tbl_dietplans d on t.diet_id=d.diet_id"
    cursor.execute(query)
    data=cursor.fetchall()
    return render_template("user/u_recieps.html",data=data)

@app.route("/u_recipesteps/<int:diet_id>")
def u_recipesteps(diet_id):
    cursor=conn.cursor()
    query = "SELECT t.diet_id,d.dp_recipename,d.dp_image, t.st_description,t.st_ingredients FROM table_recipesteps t JOIN tbl_dietplans d ON t.diet_id = d.diet_id WHERE t.diet_id = %s;"
    cursor.execute(query,(diet_id,))
    data=cursor.fetchall()  
    return render_template("user/u_recipesteps.html", data=data)

# <==================ADD TO CART====================>
@app.route("/add_cart/<int:product_id>")
def add_cart(product_id):
    cursor = conn.cursor()
    if 'u_id' not in session:
        return redirect(url_for('u_login'))
    u_id= session['u_id']
    check_query = "SELECT * FROM table_cart WHERE u_id=%s AND product_id=%s"
    check_val = (u_id, product_id)
    cursor.execute(check_query, check_val)
    existing_cart_item = cursor.fetchone()
    if existing_cart_item:
        msg = "Product already in cart"
        return redirect(url_for('u_shopping', msg=msg))
    else:
        query = "INSERT INTO table_cart (u_id, product_id,quantity) VALUES (%s,%s,1)"
        val = (u_id, product_id)
        cursor.execute(query,val)
        conn.commit()
        cursor.close()
        return redirect(url_for('view_cart'))
    
   

@app.route("/view_cart")
def view_cart():
    cursor = conn.cursor()
    if 'u_id' not in session:
        return redirect(url_for('u_login'))
    u_id= session['u_id']
    query = "SELECT c.cart_id, p.p_name, p.p_unitprice, c.quantity, p.p_image FROM table_cart c JOIN table_product p ON c.product_id = p.product_id WHERE c.u_id = %s"
    cursor.execute(query, (u_id,))
    cart_items = cursor.fetchall()

    total_price = 0
    for item in cart_items:
        total_price += float(item[2]) * item[3]

    return render_template("user/view_cart.html", cart_items=cart_items, total_price=total_price)


@app.route("/update_cart_quantity")
def update_cart_quantity():
    if 'u_id' not in session:
        return redirect(url_for('u_login'))
    
    cart_id = request.args.get('cart_id')
    action = request.args.get('action')
    
    cursor = conn.cursor()
    if action == 'increase':
        query = "UPDATE table_cart SET quantity = quantity + 1 WHERE cart_id = %s"
    elif action == 'decrease':
        # Don't decrease below 1
        query = "UPDATE table_cart SET quantity = GREATEST(1, quantity - 1) WHERE cart_id = %s"
    
    cursor.execute(query, (cart_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for('view_cart'))


@app.route("/delete_cart_item")
def delete_cart_item():
    if 'u_id' not in session:
        return redirect(url_for('u_login'))
    
    cart_id = request.args.get('cart_id')
    cursor = conn.cursor()
    query = "DELETE FROM table_cart WHERE cart_id = %s"
    cursor.execute(query, (cart_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for('view_cart'))


@app.route("/place_order", methods=["POST"])
def place_order():
    cursor = conn.cursor()
    u_id = session.get("u_id")

    # 🔴 Safety check
    if not u_id:
        return "User not logged in"

    # 🔹 1. Get cart items
    cursor.execute("SELECT p_id, quantity FROM tbl_cart WHERE u_id = %s", (u_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        return "Cart is empty"

    # 🔹 2. Calculate total amount
    cursor.execute("""
        SELECT SUM(p.p_unitprice * c.quantity)
        FROM tbl_cart c
        JOIN tbl_products p ON c.p_id = p.p_id
        WHERE c.u_id = %s
    """, (u_id,))
    
    total = cursor.fetchone()[0] or 0
    total_amount = round(total * 1.18, 2)

    # 🔹 3. Create order
    import random
    order_number = "ORD" + str(random.randint(10000, 99999))
    order_status = "Paid"

    cursor.execute("""
        INSERT INTO tbl_orders (order_number, u_id, total_amount, order_status)
        VALUES (%s, %s, %s, %s)
    """, (order_number, u_id, total_amount, order_status))

    conn.commit()

    # 🔹 4. Get last inserted order_id
    order_id = cursor.lastrowid

    # 🔹 DEBUG
    print("ORDER ID:", order_id)
    print("CART ITEMS:", cart_items)

    # 🔹 5. Insert into order_details
    for item in cart_items:
        product_id = item[0]
        qty = item[1]

        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, qty)
            VALUES (%s, %s, %s)
        """, (order_id, product_id, qty))

    conn.commit()

    # 🔹 6. Clear cart
    cursor.execute("DELETE FROM tbl_cart WHERE u_id = %s", (u_id,))
    conn.commit()

    return redirect("/order_success")







@app.route('/payment_success_cart', methods=['POST'])
def payment_success_cart():
    try:

        data = request.get_json()
        amount = data.get('total_amount')
        user_id = session.get('u_id')

        if not user_id:
            return jsonify({'status': 'failed', 'msg': 'User not logged in'})

        cursor = conn.cursor()

        order_number = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S")

        query = """
        INSERT INTO tbl_orders (order_number, u_id, total_amount, order_status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (order_number, user_id, amount, "Paid"))
        order_id = cursor.lastrowid


        cart_query = "SELECT product_id, quantity FROM table_cart WHERE u_id=%s"
        cursor.execute(cart_query, (user_id,))
        cart_items = cursor.fetchall()

        for item in cart_items:
            product_id = item[0]
            qty = item[1]
            cursor.execute("""
                INSERT INTO order_details (order_id, product_id, qty)
                VALUES (%s, %s, %s)
            """, (order_id, product_id, qty))

        cursor.execute("DELETE FROM table_cart WHERE u_id=%s", (user_id,))

        conn.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        print(" ERROR:", e)
        return jsonify({'status': 'failed', 'error': str(e)})



@app.route("/u_view_membership")
def u_view_membership():
    cursor = conn.cursor()
    query = "SELECT * FROM tbl_membershipplans"
    cursor.execute(query)
    view_membership = cursor.fetchall()
    
    return render_template("user/u_view_membership.html", view_membership=view_membership)



# @app.route('/payment_success', methods=['POST'])
# def payment_success():
#     #print("Payment success endpoint hit")
#     if 'u_id' not in session:
#         return jsonify({"status": "failed", "message": "User not logged in"}), 401
    
#     u_id = session['u_id']
#     data = request.get_json()
#     cursor = conn.cursor()
#     print(u_id)

    
#     membership_id = data.get('membership_id')
#     tot_amount = data.get('tot_amount')
#     razorpay_payment_id = data.get('razorpay_payment_id')
#     #print(membership_id, tot_amount, razorpay_payment_id)

    
#     query = """
#     INSERT INTO tbl_sub (u_id, membership_id, amount, razorpay_payment_id) 
#     VALUES (%s, %s, %s, %s)
#     """
#     cursor.execute(query, (u_id, membership_id, tot_amount, razorpay_payment_id))
#     conn.commit()
#     return jsonify({"status": "success"})
    


@app.route('/payment_success', methods=['POST'])
def payment_success():
    if 'u_id' not in session:
        return jsonify({"status": "failed", "message": "User not logged in"}), 401

    u_id = session['u_id']
    data = request.get_json()
    cursor = conn.cursor()

    membership_id = data.get('membership_id')
    tot_amount = data.get('tot_amount')
    razorpay_payment_id = data.get('razorpay_payment_id')

    # Step 1: Get duration in months
    duration_query = """
        SELECT mp_durationmonths 
        FROM tbl_membershipplans 
        WHERE membership_id = %s
    """
    cursor.execute(duration_query, (membership_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"status": "failed", "message": "Invalid membership"}), 400

    duration_months = result[0]

    # Step 2: Calculate expiry date
    current_date = datetime.now()
    expired_date = current_date + relativedelta(months=duration_months)

    # Step 3: Insert into tbl_sub
    insert_query = """
        INSERT INTO tbl_sub 
        (u_id, membership_id, amount, razorpay_payment_id, expired_date) 
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        u_id, membership_id, tot_amount, razorpay_payment_id, expired_date
    ))

    conn.commit()

    return jsonify({"status": "success"})




@app.route("/a_view_all_memberships")
def a_view_all_memberships():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
        
    cursor = conn.cursor()
    query = """
        SELECT r.u_name, m.mp_planname, s.created_date, s.expired_date
        FROM tbl_sub s
        JOIN tbl_u_registration r ON s.u_id = r.u_id
        JOIN tbl_membershipplans m ON s.membership_id = m.membership_id
        ORDER BY s.created_date DESC
    """
    cursor.execute(query)
    memberships_db = cursor.fetchall()
    
    # Process the data to calculate status
    memberships = []
    current_date = datetime.now().date()
    for m in memberships_db:
        uname = m[0]
        plan = m[1]
        
        # safely handle datetime objects versus string dates
        purchase = m[2].date() if isinstance(m[2], datetime) else m[2]
        
        # Check if python needs to parse missing datatypes directly
        expiry = m[3] if m[3] else current_date
        if isinstance(expiry, datetime):
            expiry = expiry.date()
            
        status = "Active"
        try:
            if expiry < current_date:
                status = "Expired"
            elif (expiry - current_date).days <= 5:
                status = "Expiring Soon"
        except Exception:
            pass # fallback if type error on parsing dates
            
        memberships.append({
            'user_name': uname,
            'plan_name': plan,
            'purchase_date': purchase,
            'expiry_date': expiry,
            'status': status
        })
        
    return render_template("admin/view_all_memberships.html", memberships=memberships)


if __name__ == "__main__":
    app.run(debug=True)


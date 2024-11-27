from flask import Flask, render_template, url_for, request, redirect, flash
from models import db, Todo, Project
import os
from datetime import datetime
from flask import current_app
from sqlalchemy import asc, desc



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/assignment', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('/assignment/index.html', tasks=tasks)



@app.route('/final_project', methods=['POST', 'GET'])
def form():
    if request.method == 'POST':
        try:
            # Get form data
            task = request.form['pTask']
            category = request.form['task_type']
            priority = int(request.form['pr'])
            due_date_str = request.form['due_date']
            file = request.files['file_upload']

            # Convert due_date_str to datetime.date
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

            # Ensure UPLOAD_FOLDER is defined
            UPLOAD_FOLDER = 'static/uploads'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            # Save uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Create a new project instance
            new_project = Project(
                task=task,
                category=category,
                priority=priority,
                due_date=due_date,
                file_name=file.filename
            )

            # Save to the database
            db.session.add(new_project)
            db.session.commit()

            return redirect('/final_project')

        except Exception as e:
            return f'There was an issue adding your project: {e}'

    else:
        # Fetch all projects to display
        projects = Project.query.order_by(Project.date_created).all()
        return render_template('/final_project/Form.html', projects=projects)


# Delete and update paths

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment')
    except:
        return 'There was a problem deleting that task'
    
@app.route('/delete_form/<int:id>', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/final_project')  # Redirect back to the project list

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/assignment')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('/assignment/update.html', task=task)
    

@app.route('/update_form/<int:id>', methods=['GET', 'POST'])
def Formupdate(id):
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        # Update fields from the form
        project.task = request.form['pTask']
        project.category = request.form['task_type']
        project.priority = int(request.form['pr'])
        project.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()

        # Handle file upload
        file = request.files.get('file_upload')  # Use .get() to avoid KeyError
        if file and file.filename:  # Check if a file was uploaded
            # Define the upload folder (relative to the Flask app's static folder)
            UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

            # Save the file to the upload folder
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Update the file name in the database
            project.file_name = file.filename

        try:
            # Commit changes to the database
            db.session.commit()
            return redirect('/final_project')
        except Exception as e:
            return f"There was an issue updating your project: {e}"

    return render_template('/final_project/Form_update.html', project=project)


@app.route('/final_project')
def table_route():
    # Default sorting parameters
    sort_column = request.args.get('sort_column', 'id')  # Default column to sort by
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order (ascending)

    # Dynamically determine sort order
    if sort_order == 'desc':
        sort_query = getattr(Project, sort_column).desc()
    else:
        sort_query = getattr(Project, sort_column).asc()

    # Query the database and sort
    projects = Project.query.order_by(sort_query).all()

    # Pass sorted data to the template
    return render_template('Form.html', projects=projects, sort_column=sort_column, sort_order=sort_order)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

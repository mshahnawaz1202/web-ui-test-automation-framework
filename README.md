# Django Blog App

![Blog App Banner](https://i.imgur.com/oN71fj9.jpg)

### Demo 🎥

![BlogApp Demo](https://i.imgur.com/mpntklM.gif)

### Development 👨‍💻
**Note:** Use Python 3.12 for the recommended Windows setup.

### Windows Environment Setup 🚀

Open PowerShell in the project directory.

Create a virtual environment:

```powershell
py -3.12 -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, enable it for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Apply database migrations:

```powershell
python manage.py migrate
```

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Enter your desired username, email and password. Make sure you remember them as you'll need them in future.

eg.

    Username: admin

    Email: admin@admin.com

    Password: HighlyConfidentialPassword

Start the Django development server:

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

To stop the server, press `Ctrl+C` in PowerShell.

To exit the virtual environment:

```powershell
deactivate
```

# ByteBucket

ByteBucket is a simple, user-friendly file upload and storage web application that allows users to upload files securely and manage them with ease. Built with a focus on simplicity and functionality, ByteBucket provides users with a clean and intuitive interface for storing and managing their files online.

## Features

- **File Upload**: Upload multiple types of files securely.
- **Easy File Management**: View uploaded files with details like file name, size, and type.
- **Responsive Design**: Mobile and desktop-friendly design to access ByteBucket from any device.
- **User Authentication**: User login and registration to manage your files.
- **File Deletion**: Ability to delete files after upload.
- **Real-time Updates**: Instant updates after each file upload or deletion.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **File Storage**: Local file system (or can be extended to use cloud storage services like AWS S3)
- **Authentication**: Flask-Login or Flask-JWT-Extended for token-based authentication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Naman0807/ByteBucket.git
```

2. Navigate into the project directory:
```bash
cd ByteBucket
```
 
3. Create a virtual environment:
```bash
python -m venv venv
```


4. Activate the virtual environment:
- For **Windows**:
  ```
  venv\Scripts\activate
  ```
- For **Mac/Linux**:
  ```
  source venv/bin/activate
  ```

5. Install the required dependencies:
```bash
pip install -r requirements.txt
```


6. Set up environment variables:
- Create a `.env` file in the root directory and define the following:
  ```
  FLASK_APP=app.py
  FLASK_ENV=development
  SECRET_KEY=<Your Secret Key>
  MONGO_URI=<Your MongoDB URI>
  ```

7. Run the application:
```bash
flask run
```


8. Open your browser and navigate to `http://localhost:5000` to start using ByteBucket.

## Usage

1. **Login/Register**: Sign in or register a new account to start uploading files.
2. **Upload Files**: Use the upload button to select and upload files. Supported file types include `.txt`, `.pdf`, `.jpg`, `.png`, `.mp4`, etc.
3. **Manage Files**: View uploaded files in your dashboard. Delete files that you no longer need.
4. **Authentication**: Use the built-in authentication system to keep your files private and secure.

## Contributing

Contributions are welcome! If you'd like to improve the project, feel free to submit a pull request. Here’s how you can contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit (`git commit -am 'Add Your Feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.



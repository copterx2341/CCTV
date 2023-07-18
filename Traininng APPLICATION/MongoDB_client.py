from pymongo import MongoClient
import os,time
from datetime import datetime, timezone
from PIL import Image

#Connect To MongoDB
def mongo_connect(connect_IP):
    try:
        conn = MongoClient(connect_IP)
        print("MongoDB Connected\n", conn)
        return conn

    except Exception as err:
        print(f"Error in mongodb connection: {err}")

#Upload File To MongoDB
def upload_file(file_loc, fs):
    file_name = os.path.basename(file_loc)  # Extract the file name from the file location
    
    existing_file = fs.find_one({"filename": file_name})
    if existing_file:
        fs.delete(existing_file._id)  # Delete the existing file
    
    with open(file_loc, 'rb') as file_data:
        data = file_data.read()

    fs.put(data, filename=file_name)
    print("upload complete")

def upload_file_here(file_name, fs):
    existing_file = fs.find_one({"filename": file_name})
    if existing_file:
        fs.delete(existing_file._id)  # Delete the existing file
    
    with open(file_name, 'rb') as file_data:
        data = file_data.read()

    fs.put(data, filename=file_name)
    print("upload complete")


#Download File From MongoDB
def download_file(db, fs, file_name):
    download_loc = os.path.join(os.path.dirname(__file__), file_name)

    if os.path.exists(download_loc):
        os.remove(download_loc)  # Delete the file if it already exists

    data = db.files.files.find_one({"filename": file_name})

    if data:
        fs_id = data['_id']
        out_data = fs.get(fs_id).read()

        with open(download_loc, 'wb') as output:
            output.write(out_data)
        print("Download complete")
    else:
        print("File not found in MongoDB")


#Check face.yml file if it modified or no
def check_face_yml_modified(fs):
    file_doc = fs.find_one({"filename": "face.yml"})
    if file_doc is not None:
        local_file_path = os.path.join(os.getcwd(), "face.yml")
        remote_file_size = file_doc.length
        if os.path.exists(local_file_path):
            local_file_size = os.path.getsize(local_file_path)
            if local_file_size != remote_file_size:
                # The remote "face.yml" file has been modified, delete the local file and download it again
                os.remove(local_file_path)  # Delete the local file
                with open(local_file_path, "wb") as file:
                    file.write(fs.get(file_doc._id).read())
                return True
            else:
                # File not modified
                return False

#check on the begining have face.yml or no
def check_face_yml_start(fs):
    while True:
        file_doc = fs.find_one({"filename": "face.yml"})
        if file_doc is not None:
            local_file_path = os.path.join(os.getcwd(), "face.yml")
            # if file is in local folder
            if os.path.exists(local_file_path):
                print("File Found")
                return True
            else:
                # The local "face.yml" file doesn't exist, download it from MongoDB
                with open(local_file_path, "wb") as file:
                    file.write(fs.get(file_doc._id).read())
                print("Downloaded face.yml file")
                return True
        else:
            print("face.yml file not found in MongoDB")
            time.sleep(1)  # Add a delay of 1 second before retrying

#download all jpg from database
def download_all_jpg_files(fs, destination_dir):
    # Query for all ".jpg" files in the collection
    query = {"filename": {"$regex": "\.jpg$"}}
    files = fs.find(query)

    # Iterate over the files and download them to the destination directory
    for file in files:
        filename = file.filename
        file_id = file._id
        file_path = os.path.join(destination_dir, filename)

        # Check if the file already exists in the destination directory
        if os.path.exists(file_path):
            print(f"File '{filename}' already exists in the destination directory. Skipping download.")
            continue

        # Open a new file to write the downloaded data
        with open(file_path, 'wb') as f:
            # Retrieve the file data in chunks and write them to the output file
            data = fs.get(file_id).read()
            f.write(data)

    print("Files downloaded successfully.")



def upload_all_jpg_files(directory, fs):
    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.jpg') and os.path.isfile(file_path):
            # Check if the file already exists in the GridFS collection
            if fs.find_one({"filename": filename}):
                print(f"File '{filename}' already exists in the GridFS collection. Skipping upload.")
                continue

            # Read the file data
            with open(file_path, 'rb') as f:
                # Upload the file to the GridFS collection
                fs.put(f, filename=filename)

    print("Files uploaded successfully.")

def delete_and_load_all_jpg_files(fs, destination_dir):
    # Delete existing JPG files in the destination directory
    for file_name in os.listdir(destination_dir):
        if file_name.endswith('.jpg'):
            file_path = os.path.join(destination_dir, file_name)
            os.remove(file_path)

    # Query for all ".jpg" files in the collection
    query = {"filename": {"$regex": "\.jpg$"}}
    files = fs.find(query)

    # Iterate over the files and download them to the destination directory
    for file in files:
        filename = file.filename
        file_id = file._id
        file_path = os.path.join(destination_dir, filename)

        # Open a new file to write the downloaded data
        with open(file_path, 'wb') as f:
            # Retrieve the file data in chunks and write them to the output file
            data = fs.get(file_id).read()
            f.write(data)

    print("Files downloaded successfully.")

def delete_and_upload__all_jpg_files(directory, fs):
    # Get the underlying MongoDB collection associated with GridFS
    collection = fs._GridFS__files

    # Drop the entire collection
    collection.drop()

    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('.jpg') and os.path.isfile(file_path):
            # Read the file data
            with open(file_path, 'rb') as f:
                # Upload the file to the GridFS collection
                fs.put(f, filename=filename)

    print("Files uploaded successfully.")



"""def resize_images_in_directory(directory, new_width, new_height):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            file_path = os.path.join(directory, filename)
            resize_image(file_path, new_width, new_height)

def resize_image(file_path, new_width, new_height):
    # Open the image file
    image = Image.open(file_path)

    # Resize the image
    resized_image = image.resize((new_width, new_height))

    # Overwrite the original image file
    resized_image.save(file_path)
"""
"""
import gridfs
if __name__ == '__main__':
    connection_string = "mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority"
    file_name = "face.yml"
    file_loc = "C:\\Users\\User\\OneDrive\\Desktop\\IPCamera\\Project\\Complete Code\\"
    down_loc = os.path.join(os.getcwd(), file_name)
    client = mongo_connect("mongodb+srv://chalakornter:copter2341@facemodel.ybtvagw.mongodb.net/?retryWrites=true&w=majority")
    db = client.facemodel
    fs = gridfs.GridFS(db, collection = "files")
    imgs = gridfs.GridFS(db, collection = "test_images")
    #upload_file(file_name , fs)
    #download_file(db, fs, file_name)
    #download_all_jpg_files(fs,"datasets")
    #upload_all_jpg_files("datasets", imgs)
    #download_all_jpg_files(imgs, "datasets")
    #delete_and_load_all_jpg_files(imgs,"datasets")
    delete_and_upload__all_jpg_files("datasets",imgs)
    #resize_images_in_directory("datasets", 200, 200)
"""


"""
    file_doc = fs.find_one({"filename": "face.yml"})
    if file_doc is not None:
        local_file_path = os.path.join(os.getcwd(), "face.yml")
        remote_file_timestamp = file_doc.upload_date.replace(tzinfo=timezone.utc).timestamp()
        if os.path.exists(local_file_path):
            local_file_timestamp = os.path.getmtime(local_file_path)
            local_file_datetime = datetime.fromtimestamp(local_file_timestamp, timezone.utc)
            if local_file_datetime < datetime.fromtimestamp(remote_file_timestamp, timezone.utc):
                # The remote "face.yml" file has been modified, delete the local file and download it again
                os.remove(local_file_path)  # Delete the local file
                with open(local_file_path, "wb") as file:
                    file.write(fs.get(file_doc._id).read())
                    print("File Update")
            else:
                print("Local face.yml file is up to date")
        else:
            # The local "face.yml" file doesn't exist, download it from MongoDB
            with open(local_file_path, "wb") as file:
                file.write(fs.get(file_doc._id).read())
            print("Downloaded face.yml file")
    else:
        print("face.yml file not found in MongoDB")
"""
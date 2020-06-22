from google.cloud import storage
class GoogleStorageManager:
    
    CLOUD_STORAGE_BUCKET = "frendsend.appspot.com"

    def __init__(self):
        self.gcs = storage.Client()
        self.bucket = self.gcs.get_bucket(self.CLOUD_STORAGE_BUCKET)

    def upload_file(self, uploaded_file, filename):    
        blob = self.bucket.blob(filename)
        blob.upload_from_file(uploaded_file)
        return blob.public_url
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { storage, auth } from '../config/firebase';

export const firebaseStorage = {
  uploadResume: async (file: File): Promise<string> => {
    try {
      // Check authentication
      if (!auth.currentUser) {
        console.error('Authentication error: No current user');
        throw new Error('User must be authenticated to upload files');
      }

      // Validate file
      if (!file || !(file instanceof File)) {
        console.error('Invalid file object:', file);
        throw new Error('Invalid file object');
      }

      if (file.type !== 'application/pdf') {
        console.error('Invalid file type:', file.type);
        throw new Error('Only PDF files are allowed');
      }

      if (file.size > 5 * 1024 * 1024) {
        console.error('File too large:', file.size);
        throw new Error('File size must be less than 5MB');
      }

      const userId = auth.currentUser.uid;
      const fileName = `${Date.now()}-${file.name}`;
      const filePath = `resumes/${userId}/${fileName}`;
      const storageRef = ref(storage, filePath);

      console.log('Attempting to upload file:', {
        name: file.name,
        size: file.size,
        type: file.type,
        path: filePath
      });

      // Upload the file
      const snapshot = await uploadBytes(storageRef, file);
      console.log('File uploaded successfully:', snapshot.metadata);
      
      // Get the download URL
      const downloadURL = await getDownloadURL(storageRef);
      console.log('File download URL obtained:', downloadURL);
      
      return downloadURL;
    } catch (error: any) {
      console.error('Detailed upload error:', {
        error,
        errorCode: error.code,
        errorMessage: error.message,
        errorDetails: error.serverResponse
      });
      
      // Provide more specific error messages
      if (error.code === 'storage/unauthorized') {
        throw new Error('Permission denied: Please check if you are logged in');
      } else if (error.code === 'storage/canceled') {
        throw new Error('Upload was cancelled');
      } else if (error.code === 'storage/quota-exceeded') {
        throw new Error('Storage quota exceeded');
      } else {
        throw new Error(`Failed to upload resume: ${error.message}`);
      }
    }
  }
}; 
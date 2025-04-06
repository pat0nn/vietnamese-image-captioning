# Image Captioning App

This project consists of a Flask backend API that processes uploaded images and generates captions using a pre-trained vision-language model, and a Next.js frontend for uploading images and displaying captions. It also includes a feature for users to contribute data by uploading images and providing their own captions.

## Project Structure

```
image-uploader/
├── backend/
│   ├── app.py          # Flask API for image captioning
│   ├── requirements.txt # Python dependencies
│   ├── uploads/        # Directory for stored images
│   └── .gitignore      # Git ignore for backend
├── docker-compose.yml  # Docker configuration for PostgreSQL
└── frontend/           # Next.js frontend application
    ├── components/     # React components
    ├── pages/          # Next.js pages
    ├── public/         # Static assets
    ├── styles/         # CSS styles
    └── package.json    # Node dependencies
```

## Database Setup

1. Start the PostgreSQL database using Docker:
   ```
   cd image-uploader
   docker-compose up -d
   ```

   This will start a PostgreSQL database container accessible at `localhost:5432`.

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd image-uploader/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd image-uploader/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`.

## How It Works

### AI Caption Mode

1. Upload an image through the frontend interface
2. The image is sent to the backend API
3. The backend processes the image using the pre-trained vision-language model
4. A caption is generated and returned to the frontend
5. The frontend displays the image and its caption

### Contribution Mode

1. Switch to "Contribution Mode" using the toggle button
2. Upload an image through the frontend interface
3. Enter your own caption for the image in the text area
4. Click "Save Contribution" to save the image and caption
5. The image and caption are stored in the PostgreSQL database
6. The data can be used for training or evaluation purposes

## Model Information

The image captioning model used is based on:
- VisionEncoderDecoderModel with ViT image encoder and BARTpho text decoder
- Trained to generate Vietnamese captions for images

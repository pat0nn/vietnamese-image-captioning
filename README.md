# Vietnamese Automatic Image Captioning System

## 🎓 Graduation Project

A project developing an automatic image captioning system based on **Vision Transformer (ViT)** and **BARTpho** to generate accurate Vietnamese descriptions for images automatically.

## 📋 Project Description

The system uses advanced AI technology to analyze images and generate natural Vietnamese descriptions. The project combines:

- **Vision Transformer (ViT)**: Powerful encoder model for extracting features from images
- **BARTpho**: Specialized decoder model for Vietnamese text to generate natural descriptions
- **Web Application**: User-friendly interface for interacting with the system

## 🏗️ System Architecture

```
vietnamese-image-captioning/
├── frontend-vue/          # Frontend - User Interface
├── backend/              # Backend API - Processing Server
├── vit-bartpho-model/    # AI Model - ViT-BARTpho Model
├── fixed_dump.sql        # Database Schema
└── README.md            # Project Documentation
```

## 🚀 Technologies Used

### Frontend
- **Vue.js 3** - Modern JavaScript framework
- **Vite** - Fast and efficient build tool
- **Tailwind CSS** - Styling framework
- **Pinia** - State management
- **Vue Router** - Routing
- **Axios** - HTTP client
- **ApexCharts** - Charts and statistics

### Backend
- **Python Flask** - Web framework
- **PostgreSQL** - Database
- **JWT Authentication** - User authentication
- **Docker** - Containerization
- **Nginx** - Web server

### AI Model
- **PyTorch** - Deep learning framework
- **Transformers (Hugging Face)** - Pre-trained models
- **Vision Transformer (ViT)** - Image encoder
- **BARTpho** - Vietnamese text decoder
- **Weights & Biases** - Experiment tracking

## ✨ Key Features

### 🖼️ Image Captioning
- Upload and process images
- Generate automatic Vietnamese descriptions
- Display results with confidence scores
- Support batch processing

### 👥 User Management
- User registration and login
- Admin and user role permissions
- Activity history
- Personal profiles

### ⭐ Rating & Contribution
- Rate caption quality (1-5 stars)
- User caption contributions
- Review and approval system
- Rating statistics

### 📊 Statistics & Analytics
- Daily usage statistics
- Admin dashboard
- Model performance reports
- User analytics

## 🛠️ Installation and Setup

### System Requirements
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### 1. Clone Repository
```bash
git clone <repository-url>
cd vietnamese-image-captioning
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Configure database in app/config/settings.py
# Run database migrations
python fix_sequence.py

# Start server
python run.py
```

### 3. Frontend Setup
```bash
cd frontend-vue
npm install

# Development
npm run dev

# Production build
npm run build
```

### 4. AI Model Setup
```bash
cd vit-bartpho-model
pip install -r requirements.txt

# Train model
python main.py --mode train --use_wandb

# Inference
python main.py --mode inference --image_path path/to/image.jpg
```

### 5. Run with Docker
```bash
# Backend
cd backend
docker-compose up

# Frontend
cd frontend-vue
docker build -t frontend-vue .
docker run -p 80:80 frontend-vue
```

## 📊 Model Evaluation

The model is evaluated using standard metrics:
- **BLEU Score**: Measures vocabulary accuracy
- **ROUGE Score**: Measures semantic similarity
- **METEOR Score**: Comprehensive evaluation
- **CIDEr Score**: Specialized metric for image captioning

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/user` - Get user information

### Image Captioning
- `POST /api/caption` - Generate caption for image
- `GET /api/images` - Get list of images

### Rating & Contribution
- `POST /api/rate/<image_id>` - Rate caption
- `POST /api/contribute` - Contribute caption
- `GET /api/contributions` - View contributions

### Admin
- `GET /api/admin/users` - Manage users
- `GET /api/admin/contributions/pending` - Review contributions
- `GET /api/admin/stats` - System statistics

## 📝 Database Schema

### Main Tables:
- **users**: User information
- **images**: Image data and captions
- **caption_ratings**: Quality ratings
- **contributions**: User contributions
- **model_versions**: Model versions
- **daily_stats**: Daily statistics

## 🚦 Workflow

1. **Upload Image**: User uploads an image
2. **Image Processing**: System processes and extracts features
3. **Caption Generation**: ViT-BARTpho model generates caption
4. **Result Display**: Display results to user
5. **User Feedback**: Collect ratings and contributions
6. **Model Improvement**: Use feedback to improve model

## 📈 Experimental Results

- **BLEU-4 Score**: [Fill in results]
- **ROUGE-L Score**: [Fill in results]
- **Human Evaluation**: [Fill in results]
- **Inference Speed**: [Fill in timing]

## 🤝 Contributing

To contribute to the project:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Create a Pull Request

## 📄 License

[Fill in license information]

## 👥 Authors

**[Student Name]**
- Email: [Email]
- Faculty: [Faculty Name]
- University: [University Name]
- Year: [Academic Year]

**Supervisor**: [Supervisor Name]

## 📞 Contact

- Email: [Contact Email]
- GitHub: [GitHub profile]
- LinkedIn: [LinkedIn profile]

---

> 💡 **Note**: This is a graduation thesis project developed for research and educational purposes. All feedback and contributions are welcome! 
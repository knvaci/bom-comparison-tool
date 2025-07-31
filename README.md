# 🚀 BOM Comparison Tool

A powerful web-based tool for comparing Bill of Materials (BOM) Excel files with intelligent column detection and comprehensive analysis.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **🔍 Intelligent Column Detection**: Automatically detects MPN, Quantity, Ref Des, and Description columns
- **📊 Side-by-Side Comparison**: Visual comparison with color-coded categories
- **🎯 5 Category Analysis**: 
  - 🟢 **Category 1**: Parts present in both files
  - 🔵 **Category 2**: Parts only in file 1
  - 🟢 **Category 3**: Parts only in file 2
  - 🟡 **Category 4**: Parts with data differences
  - ⚫ **Category 5**: Unrecognized parts
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🗄️ Database Integration**: PostgreSQL support with Docker
- **🧪 Comprehensive Testing**: QA testing framework included

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker Desktop (for PostgreSQL)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bom-comparison-tool.git
   cd bom-comparison-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database with Docker**
   ```bash
   python setup_docker_postgres.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
excel_tool/
├── 📁 src/                          # Source code package
│   ├── 📁 database/                 # Database models
│   └── 📁 utils/                    # Utility functions
├── 📁 scripts/                      # Setup scripts
├── 📁 test_files/                   # Excel test files
├── 🌐 app.py                        # Flask application
├── 🔧 excel_tool.py                 # Core logic
└── 🐳 docker-compose.yml            # Docker setup
```

## 🧪 Testing

### Manual Testing
Follow the comprehensive [QA Testing Guide](QA_TESTING_GUIDE.md) for detailed testing instructions.

### Automated Testing
```bash
python scripts/run_tests.py
```

## 🐳 Docker Support

The project includes Docker support for PostgreSQL:

```bash
# Start PostgreSQL container
docker-compose up -d

# Stop container
docker-compose down

# View logs
docker-compose logs postgres
```

## 📊 Supported File Formats

- **Excel**: `.xlsx`, `.xls`
- **Column Detection**: MPN, Quantity, Ref Des, Description
- **File Size**: Up to 16MB per file

## 🔧 Configuration

Key configuration options in `config.py`:

- Database connection settings
- File upload limits
- Logging configuration
- Development/production modes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [QA Testing Guide](QA_TESTING_GUIDE.md)
2. Review the [Project Structure](PROJECT_STRUCTURE.md)
3. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Export comparison results to Excel
- [ ] Batch file processing
- [ ] Advanced filtering options
- [ ] User authentication
- [ ] API endpoints for integration

---

**Made with ❤️ for BOM analysis** 
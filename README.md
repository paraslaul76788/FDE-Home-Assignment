# Creative Automation Pipeline

A proof-of-concept system that automatically generates social media creatives from campaign briefs using AI. The pipeline creates multiple aspect ratio variations for different social media platforms.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
# Clone the repo to your local machine
git clone https://github.com/paraslaul76788/FDE-Home-Assignment.git

# Navigate to the project directory
cd FDE-Home-Assignment
```

### 2. Install Dependencies

Install required Python packages using pip
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
echo "HUGGINGFACE_API_KEY=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" > .env
```

### 4. Run the Pipeline

```bash
python3 main.py
```

## 🏗️ Key Design Decisions

### 1. Asset-First Approach

- **Decision**: Check for existing assets before generating new ones

- **Rationale**: Maximizes efficiency and cost savings by reusing available resources

- **Implementation**: get_existing_asset_path() method with multiple file extension support

### 2. Modular Pipeline Architecture

- **Decision**: Separate concerns into distinct processing stages

- **Rationale**: Enables easy testing, maintenance, and future extensions

- **Components**:

        Campaign Brief Parser

        Asset Manager

        AI Generator

        Creative Engine

        Output Organizer

## 3. Config-Driven Design

- **Decision**: Externalize all configuration parameters

- **Rationale**: Allows customization without code changes

- **Configurable Elements**:

      Aspect ratios and dimensions

      AI model priorities

      File paths and directories

      API timeouts and retry logic

## 5. Structured Output Organization

- **Decision**: Hierarchical folder structure by product and format

- **Rationale**: Enables easy asset management and platform-specific distribution

- **Structure**: output/{product_id}/{aspect_ratio}/creative_{ratio}.jpg

## ⚙️ Assumptions

### Technical Assumptions

**File System Access**: Application has read/write permissions to current directory

**Internet Connectivity**: Required for AI generation (optional for asset reuse)

**Image Formats**: Supports common formats (JPEG, PNG, WebP) for input assets

**Memory Constraints**: Handles typical product image sizes without excessive memory usage

### Business Assumptions

**Campaign Structure**: Campaigns contain multiple products with clear identifiers

**Asset Naming**: Existing assets follow predictable naming conventions ({product_id}.{ext})

**Output Requirements**: Three standard aspect ratios cover most social media needs

**Text Overlay**: Campaign messages are concise enough for image overlays

### API Assumptions

**Service Availability**: AI services may have rate limits or downtime

**Cost Considerations**: AI generation has associated costs, hence asset reuse priority

**Response Format**: AI services return images in compatible formats

## ⚠️ Limitations
### Current Limitations**
**AI Dependency**: Requires working AI API for new asset generation

**Single Language**: Campaign messages in English only

**Basic Text Overlay**: Simple text positioning without advanced typography

**Image-Only**: Supports static images only (no video or animated content)

**Local Storage**: Outputs to local file system only (no cloud integration)

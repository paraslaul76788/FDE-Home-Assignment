import json
import os
import logging
from PIL import Image, ImageDraw, ImageFont
import requests
import time
from config import Config

class CreativeAutomationPipeline:
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        
    def setup_logging(self):
        """Initialize logging configuration for the pipeline"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_campaign_brief(self, brief_path):
        """Load campaign brief from JSON file containing product details and campaign info"""
        try:
            with open(brief_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading campaign brief: {e}")
            raise
            
    def get_existing_asset_path(self, product_id):
        """Check if assets already exist for a product in input_assets folder
        Returns file path if found, None otherwise"""
        possible_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for ext in possible_extensions:
            asset_path = os.path.join(self.config.INPUT_ASSETS_DIR, f"{product_id}{ext}")
            if os.path.exists(asset_path):
                self.logger.info(f"Found existing asset: {asset_path}")
                return asset_path
        
        self.logger.info(f"No existing asset found for: {product_id}")
        return None
    
    def generate_with_huggingface(self, product, campaign_brief):
        """Generate product image using Hugging Face AI models
        Tries multiple models in sequence until one works"""
        
        for model in self.config.HUGGINGFACE_MODELS:
            try:
                API_URL = f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}"}
                
                # Create prompt for AI image generation
                prompt = f"professional product photo of {product['name']}, {product['description']}, clean white background, high quality, advertising photography, studio lighting"
                
                self.logger.info(f"Trying model: {model}")
                response = requests.post(API_URL, headers=headers, json={
                    "inputs": prompt,
                    "options": {"wait_for_model": True}
                }, timeout=120)
                
                if response.status_code == 200:
                    # Save generated image to assets folder
                    os.makedirs(self.config.INPUT_ASSETS_DIR, exist_ok=True)
                    asset_path = os.path.join(self.config.INPUT_ASSETS_DIR, f"{product['id']}.jpg")
                    
                    with open(asset_path, 'wb') as f:
                        f.write(response.content)
                    
                    self.logger.info(f"Successfully generated image with {model}")
                    return asset_path
                else:
                    self.logger.warning(f"Model {model} API error: {response.status_code}")
                    continue
                    
            except Exception as e:
                self.logger.warning(f"Model {model} failed: {e}")
                continue
        
        return None
    
    def generate_product_image(self, product, campaign_brief):
        """Main method to generate product image using available GenAI services
        Implements fallback strategy between different AI providers"""
        self.logger.info(f"Generating new asset for: {product['name']}")
        
        for service in self.config.AI_PRIORITY:
            try:
                if service == 'huggingface' and self.config.HUGGINGFACE_API_KEY:
                    self.logger.info("Trying Hugging Face models...")
                    generated_path = self.generate_with_huggingface(product, campaign_brief)
                    if generated_path:
                        return generated_path
                        
            except Exception as e:
                self.logger.warning(f"Service {service} failed: {e}")
                continue
                
            time.sleep(2)  # Brief pause between service attempts
        
        # If all AI services fail, raise exception
        raise Exception(f"All GenAI services failed for product: {product['name']}")

    def resize_image_for_aspect_ratio(self, image_path, aspect_ratio, dimensions):
        """Resize source image to specific aspect ratio dimensions
        Used to create different formats for social media platforms"""
        try:
            with Image.open(image_path) as img:
                img = img.resize(dimensions, Image.Resampling.LANCZOS)
                return img
        except Exception as e:
            self.logger.error(f"Error resizing image: {e}")
            return None

    def add_campaign_message(self, image, campaign_message, aspect_ratio):
        """Add campaign message text overlay to the image
        Adjusts font size and position based on aspect ratio"""
        try:
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Adjust text positioning based on aspect ratio
            if aspect_ratio == '9_16':
                font_size = 40
                text_position = (50, image.height - 100)  # Bottom left for vertical
            elif aspect_ratio == '16_9':
                font_size = 50
                text_position = (100, image.height - 80)  # Bottom center for horizontal
            else:  # 1:1
                font_size = 45
                text_position = (60, image.height - 90)   # Bottom for square
            
            # Try to load system fonts, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Create text background for better readability
            bbox = draw.textbbox(text_position, campaign_message, font=font)
            padding = 10
            draw.rectangle(
                [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding],
                fill='white'
            )
            
            # Add campaign message text
            draw.text(text_position, campaign_message, fill='black', font=font)
            return img_with_text
            
        except Exception as e:
            self.logger.error(f"Error adding campaign message: {e}")
            return image

    def generate_creatives(self, campaign_brief_path):
        """Main pipeline method that orchestrates the entire creative generation process
        Steps: Load brief → Check/generate assets → Create multi-format creatives → Save outputs"""
        self.logger.info("Starting creative generation pipeline...")
        
        # Load campaign configuration
        campaign_brief = self.load_campaign_brief(campaign_brief_path)
        self.logger.info(f"Loaded campaign: {campaign_brief['campaign_name']}")
        
        # Initialize results tracking
        results = {
            'campaign': campaign_brief['campaign_name'],
            'products_processed': 0,
            'assets_generated': 0,
            'generation_methods': []
        }
        
        # Process each product in the campaign
        for product in campaign_brief['products']:
            self.logger.info(f"Processing product: {product['name']}")
            
            # CHECK FOR EXISTING ASSETS FIRST (Primary requirement)
            existing_asset_path = self.get_existing_asset_path(product['id'])
            
            if existing_asset_path:
                # USE EXISTING ASSET - Reuse when available
                asset_path = existing_asset_path
                method = "existing_asset"
                self.logger.info(f"Using existing asset: {asset_path}")
            else:
                # GENERATE NEW WITH GENAI - Create when missing (Secondary requirement)
                self.logger.info(f"No existing asset found, generating with GenAI...")
                asset_path = self.generate_product_image(product, campaign_brief)
                method = "genai_generated"
            
            # Process asset if successfully obtained
            if asset_path and os.path.exists(asset_path):
                # Generate creatives for all required aspect ratios
                for ratio_name, dimensions in self.config.ASPECT_RATIOS.items():
                    resized_img = self.resize_image_for_aspect_ratio(asset_path, ratio_name, dimensions)
                    
                    if resized_img:
                        # Add campaign message to resized image
                        final_img = self.add_campaign_message(
                            resized_img, 
                            campaign_brief['campaign_message'], 
                            ratio_name
                        )
                        
                        # Create organized output directory structure
                        output_dir = os.path.join(
                            self.config.OUTPUT_DIR, 
                            product['id'], 
                            ratio_name
                        )
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # Save final creative
                        output_path = os.path.join(output_dir, f"creative_{ratio_name}.jpg")
                        final_img.save(output_path, 'JPEG', quality=95)
                        
                        # Track generation results
                        results['assets_generated'] += 1
                        results['generation_methods'].append({
                            'product': product['id'],
                            'product_name': product['name'],
                            'method': method,
                            'input_asset': asset_path,
                            'output': output_path
                        })
                        
                        self.logger.info(f"Generated creative: {output_path}")
            else:
                self.logger.error(f"Failed to get asset for {product['name']}")
                continue
            
            results['products_processed'] += 1
        
        self.logger.info("Creative generation pipeline completed!")
        return results

def main():
    """Main execution function - orchestrates the entire creative automation pipeline"""
    config = Config()
    pipeline = CreativeAutomationPipeline(config)
    
    try:
        # Execute the creative generation pipeline
        results = pipeline.generate_creatives('campaign_brief.json')
        
        # Display comprehensive results summary
        print("\n" + "="*60)
        print("CREATIVE AUTOMATION PIPELINE - COMPLETED")
        print("="*60)
        print(f"Campaign: {results['campaign']}")
        print(f"Products Processed: {results['products_processed']}")
        print(f"Assets Generated: {results['assets_generated']}")
        
        # Show detailed generation methods used
        print(f"\nASSET GENERATION METHODS:")
        for method in results['generation_methods']:
            status = "🔄 GenAI Generated" if method['method'] == "genai_generated" else "✅ Existing Asset"
            print(f"  {status}: {method['product_name']}")
            print(f"     Input: {method['input_asset']}")
            print(f"     Output: {method['output']}")
        
        print(f"\nOutput Directory: {config.OUTPUT_DIR}/")
        
    except Exception as e:
        # Comprehensive error handling and troubleshooting guide
        print(f"Pipeline execution failed: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Add some sample images to input_assets/ folder:")
        print("   - input_assets/product1.jpg")
        print("   - input_assets/product2.jpg")
        print("2. Get a free Hugging Face token: https://huggingface.co/settings/tokens")
        print("3. Add your token to .env file: HUGGINGFACE_API_KEY=your_token_here")

if __name__ == "__main__":
    main()
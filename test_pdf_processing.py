import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.document_processor_fixed import FixedDocumentProcessor

async def test_pdf_processing():
    """Test the improved PDF processing with the problematic URL"""
    
    # The problematic URL
    test_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    print("🧪 Testing improved PDF processing...")
    print(f"URL: {test_url}")
    print("-" * 50)
    
    try:
        # Initialize processor
        processor = FixedDocumentProcessor()
        
        # Process the document
        result = await processor.process_with_robustness(test_url)
        
        # Check results
        if result and result.get('text'):
            text = result.get('text', '')
            print(f"✅ SUCCESS! Extracted {len(text)} characters")
            print(f"Text preview: {text[:200]}...")
            
            if "Document processing failed:" in text:
                print("⚠️  Got error message in text")
                print(f"Error: {text}")
            else:
                print("🎉 Document processed successfully!")
                
        else:
            print("❌ No text extracted")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_pdf_processing()) 
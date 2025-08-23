import streamlit as st
import requests
import json
from googletrans import Translator

def render_page():
    """Render the English to Nepali converter page"""
    
    st.title("🇳🇵 English to Nepali Translator & Font Converter")
    st.markdown("Translate English text to Nepali and convert between different Nepali font formats")
    
    # Initialize translator
    @st.cache_resource
    def get_translator():
        return Translator()

    # Kantipur to Unicode mapping (simplified version)
    kantipur_to_unicode_map = {
        'k': 'क', 'kh': 'ख', 'g': 'ग', 'gh': 'घ', 'ng': 'ङ',
        'c': 'च', 'ch': 'छ', 'j': 'ज', 'jh': 'झ', 'ny': 'ञ',
        't': 'ट', 'th': 'ठ', 'd': 'ड', 'dh': 'ढ', 'n': 'ण',
        'ta': 'त', 'tha': 'थ', 'da': 'द', 'dha': 'ध', 'na': 'न',
        'p': 'प', 'ph': 'फ', 'b': 'ब', 'bh': 'भ', 'm': 'म',
        'y': 'य', 'r': 'र', 'l': 'ल', 'w': 'व', 'sh': 'श',
        's': 'स', 'h': 'ह', 'ksh': 'क्ष', 'tr': 'त्र', 'gya': 'ज्ञ'
    }

    def convert_kantipur_to_unicode(text):
        """Simple Kantipur to Unicode converter"""
        result = text
        # Sort by length (longest first) to avoid partial replacements
        for kantipur, unicode_char in sorted(kantipur_to_unicode_map.items(), key=len, reverse=True):
            result = result.replace(kantipur, unicode_char)
        return result

    def translate_text(text, source_lang='en', target_lang='ne'):
        """Translate text using Google Translate"""
        try:
            translator = get_translator()
            translation = translator.translate(text, src=source_lang, dest=target_lang)
            return translation.text
        except Exception as e:
            return f"Translation error: {str(e)}"

    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["📝 English to Nepali", "🔤 Font Converter", "ℹ️ About"])

    with tab1:
        st.header("English to Nepali Translation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("English Input")
            english_text = st.text_area(
                "Type your English text here:",
                height=200,
                placeholder="Enter English text to translate to Nepali..."
            )
            
            if st.button("Translate to Nepali", type="primary"):
                if english_text.strip():
                    with st.spinner("Translating..."):
                        nepali_translation = translate_text(english_text)
                        st.session_state['translation'] = nepali_translation
                else:
                    st.warning("Please enter some text to translate.")
        
        with col2:
            st.subheader("Nepali Output")
            if 'translation' in st.session_state:
                st.markdown(f"""
                <div style='background-color: #f8f9ff; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; margin: 10px 0;'>
                    <div style='font-family: "Devanagari Sangam MN", "Noto Sans Devanagari", sans-serif; font-size: 18px; line-height: 1.6;'>{st.session_state['translation']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Copy button
                st.code(st.session_state['translation'], language=None)
            else:
                st.info("Translation will appear here...")

    with tab2:
        st.header("Font Converter (Kantipur/PCS to Unicode)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Input Font Text")
            font_type = st.selectbox(
                "Select Input Font:",
                ["Kantipur", "PCS Nepali", "Preeti"]
            )
            
            input_font_text = st.text_area(
                f"Paste your {font_type} text here:",
                height=200,
                placeholder=f"Paste {font_type} formatted text here..."
            )
            
            if st.button("Convert to Unicode", type="primary"):
                if input_font_text.strip():
                    if font_type == "Kantipur":
                        unicode_text = convert_kantipur_to_unicode(input_font_text)
                    else:
                        # For PCS and Preeti, you would need specific conversion libraries
                        unicode_text = "Conversion for PCS/Preeti requires specific libraries. This is a demo conversion."
                    st.session_state['converted_text'] = unicode_text
                else:
                    st.warning("Please enter some text to convert.")
        
        with col2:
            st.subheader("Unicode Output")
            if 'converted_text' in st.session_state:
                st.markdown(f"""
                <div style='background-color: #f8f9ff; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; margin: 10px 0;'>
                    <div style='font-family: "Devanagari Sangam MN", "Noto Sans Devanagari", sans-serif; font-size: 18px; line-height: 1.6;'>{st.session_state['converted_text']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.code(st.session_state['converted_text'], language=None)
            else:
                st.info("Converted text will appear here...")

    with tab3:
        st.header("About This Tool")
        
        st.markdown("""
        <div style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #e0e7ff;'>
            <h3>🌟 Features</h3>
            <ul>
                <li><strong>English to Nepali Translation:</strong> Translate English text to Nepali using Google Translate API</li>
                <li><strong>Font Conversion:</strong> Convert Kantipur, PCS Nepali, or Preeti fonts to Unicode</li>
                <li><strong>Copy-friendly Output:</strong> Easy to copy converted/translated text</li>
                <li><strong>Real-time Processing:</strong> Instant translation and conversion</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #e0e7ff;'>
            <h3>📋 How to Use</h3>
            <ol>
                <li><strong>English to Nepali:</strong> Type English text in the input box and click "Translate"</li>
                <li><strong>Font Converter:</strong> Select your font type, paste the text, and click "Convert"</li>
                <li><strong>Copy Results:</strong> Use the code box to easily copy the output text</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #e0e7ff;'>
            <h3>⚠️ Important Notes</h3>
            <ul>
                <li>For font conversion, you need the original fonts installed on your computer</li>
                <li>This is a simplified version - full PCS/Preeti conversion requires specialized libraries</li>
                <li>Translation quality depends on Google Translate API</li>
                <li>Internet connection required for translation features</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Made with ❤️ for Nepali language processing</p>", 
        unsafe_allow_html=True
    )

    # Sidebar information
    with st.sidebar:
        st.markdown("### 📦 Required Packages")
        st.code("pip install googletrans==4.0.0rc1")
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - For accurate font conversion, install the original fonts
        - Internet connection needed for translation
        - Use clear, simple English for better translations
        """) 
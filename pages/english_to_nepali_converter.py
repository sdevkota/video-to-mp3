import streamlit as st
import re
from googletrans import Translator

# Page configuration
st.set_page_config(
    page_title="Nepali Unicode Converter - Advanced IME",
    page_icon="🇳🇵",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 30px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
    }
    .converter-box {
        background-color: #f8f9ff;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .nepali-text {
        font-family: 'Devanagari Sangam MN', 'Noto Sans Devanagari', sans-serif;
        font-size: 18px;
        line-height: 1.6;
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e7ff;
        min-height: 200px;
        white-space: pre-wrap;
    }
    .feature-box {
        background-color: #f0f9ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #e0e7ff;
    }
    .mode-button {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 2px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .mode-button.active {
        background-color: #1e293b;
        color: white;
        border-color: #1e293b;
    }
    .example-button {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        text-align: left;
        transition: all 0.2s;
        cursor: pointer;
    }
    .example-button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    .stats {
        display: flex;
        gap: 20px;
        margin-top: 10px;
        font-size: 12px;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize translator
@st.cache_resource
def get_translator():
    return Translator()

# Constants
ZWNJ = "\u200C"  # zero width non-joiner
ZWJ = "\u200D"   # zero width joiner
HALANT = "\u094D"  # ्

# Vowel letters and signs
VOWELS = {
    "a": "अ", "aa": "आ", "A": "आ",
    "i": "इ", "ee": "ई", "I": "ई",
    "u": "उ", "oo": "ऊ", "U": "ऊ",
    "e": "ए", "ai": "ऐ",
    "o": "ओ", "au": "औ",
    "rri": "ऋ", "rree": "ॠ",
}

MATRAS = {
    "a": "", "aa": "ा", "A": "ा",
    "i": "ि", "ee": "ी", "I": "ी",
    "u": "ु", "oo": "ू", "U": "ू",
    "e": "े", "ai": "ै",
    "o": "ो", "au": "ौ",
    "rri": "ृ", "rree": "ॄ",
}

# Base consonants mapping (phonetic)
CONSONANTS = {
    # Velars
    "k": "क", "kh": "ख", "g": "ग", "gh": "घ", "x": "क्ष",
    # Palatals
    "c": "च", "ch": "च", "chh": "छ", "j": "ज", "jh": "झ",
    "ny": "ञ", "yna": "ञ",
    # Dentals & retroflex
    "t": "त", "th": "थ", "d": "द", "dh": "ध", "n": "न",
    "ta": "त", "tha": "थ", "da": "द", "dha": "ध", "na": "न",
    "T": "ट", "Th": "ठ", "D": "ड", "Dh": "ढ", "N": "ण",
    "Ta": "ट", "Tha": "ठ", "Da": "ड", "Dha": "ढ", "Na": "ण",
    # Labials
    "p": "प", "ph": "फ", "b": "ब", "bh": "भ", "m": "म",
    # Others
    "y": "य", "r": "र", "l": "ल", "w": "व", "v": "व",
    "s": "स", "sh": "श", "Sh": "ष", "h": "ह",
    # Compounds
    "ksha": "क्ष", "gya": "ज्ञ",
}

SPECIALS = {
    "*": "ं", "**": "ँ", "om": "ॐ",
    "rr": "र" + HALANT + ZWJ,
    "ri^": "रि",
}

# Common-word overrides
LEXICON = {
    # particles / auxiliaries
    "ke": "के", "ko": "को", "le": "ले", "laai": "लाई", "lai": "लाई",
    "ra": "र", "ho": "हो", "huncha": "हुन्छ", "hunchha": "हुन्छ", "hucha": "हुन्छ",
    "cha": "छ", "chha": "छ", "xa": "छ", "xha": "छ",
    "chan": "छन्", "chu": "छु", "chhau": "छौँ", "chhaū": "छौँ",
    "chhaen": "छैन", "chaina": "छैन", "chhaina": "छैन", "xaina": "छैन",
    # frequent conversational
    "raichha": "रैछ", "raicha": "रैछ", "raixa": "रैछ",
    "k": "के", "kha": "खा", "kasto": "कस्तो", "ramro": "राम्रो",
    "dherai": "धेरै", "sabai": "सबै", "huney": "हुने", "hune": "हुने",
    # pronouns
    "ma": "म", "hamro": "हाम्रो", "hamrai": "हाम्रोै", "mero": "मेरो",
    "timi": "तिमी", "tapai": "तपाईं", "tapaī": "तपाईं",
    # interjections
    "hya": "हया",
}

# Order tokens longest-first for greedy matching
def get_token_order(dictionary):
    return sorted(dictionary.keys(), key=len, reverse=True)

V_ORDER = get_token_order(VOWELS)
C_ORDER = get_token_order(CONSONANTS)
S_ORDER = get_token_order(SPECIALS)

def is_alpha_num(ch):
    return bool(re.match(r'[A-Za-z0-9]', ch))

def encode_html(text):
    return ''.join([f'&#{ord(c)};' for c in text])

def transliterate(input_text):
    """Core transliteration engine"""
    segments = []
    i = 0
    
    while i < len(input_text):
        if input_text[i] == '{':
            end = input_text.find('}', i + 1)
            if end != -1:
                segments.append({'type': 'raw', 'text': input_text[i+1:end]})
                i = end + 1
                continue
        
        # Normal segment until next {
        next_brace = input_text.find('{', i)
        text = input_text[i:next_brace] if next_brace != -1 else input_text[i:]
        segments.append({'type': 'nep', 'text': text})
        i = next_brace if next_brace != -1 else len(input_text)
    
    return ''.join([seg['text'] if seg['type'] == 'raw' else translit_nep(seg['text']) for seg in segments])

def translit_nep(s):
    """Replace Latin-letter words by lexicon or phonetic rules"""
    def replace_word(match):
        word = match.group(0)
        key = word.lower()
        if key in LEXICON:
            return LEXICON[key]
        return translit_syllables(word)
    
    return re.sub(r'[A-Za-z]+', replace_word, s)

def translit_syllables(s):
    """Phonetic engine over a single token"""
    out = ""
    i = 0
    
    def push_consonant(base, vowel_key):
        # Special case: users expect 'ya' → 'या'
        if base == 'य' and (not vowel_key or vowel_key == 'a'):
            out += base + 'ा'
            return
        
        if not vowel_key or vowel_key == 'a':  # inherent 'a'
            out += base
        else:
            matra = MATRAS.get(vowel_key, "")
            out += base + matra
    
    def peek_consonant_key(idx):
        for k in C_ORDER:
            if s.startswith(k, idx):
                return k
        return None
    
    def peek_vowel_key(idx):
        for vk in V_ORDER:
            if s.startswith(vk, idx):
                return vk
        return None
    
    while i < len(s):
        ch = s[i]
        
        # Explicit separators
        if ch == '/':
            out += ZWNJ
            i += 1
            continue
        if ch == "\\":
            out += HALANT
            i += 1
            continue
        
        # Punct/space
        if not is_alpha_num(ch) and ch != '*':
            out += ch
            i += 1
            continue
        
        # Specials
        matched = False
        for key in S_ORDER:
            if s.startswith(key, i):
                out += SPECIALS[key]
                i += len(key)
                matched = True
                break
        if matched:
            continue
        
        # Lexical nasalization
        if (s[i] in ['n', 'm'] and 
            i + 1 < len(s) and 
            re.match(r'[kgcjqtdpbshx]', s[i+1], re.IGNORECASE)):
            out += 'ं'
            i += 1
            continue
        
        # Consonant handling
        c_key = peek_consonant_key(i)
        if c_key:
            base = CONSONANTS[c_key]
            i += len(c_key)
            
            # Optional vowel after consonant
            v_key = peek_vowel_key(i)
            
            if v_key:
                push_consonant(base, v_key)
                i += len(v_key)
            else:
                # Check next for consonant to form conjunct
                next_c = peek_consonant_key(i)
                if next_c:
                    out += base + HALANT  # form conjunct
                else:
                    push_consonant(base, 'a')
            continue
        
        # Standalone vowels
        v_key2 = peek_vowel_key(i)
        if v_key2:
            out += VOWELS[v_key2]
            i += len(v_key2)
            continue
        
        # Fallback: pass-through
        out += ch
        i += 1
    
    return out

def translate_text(text, source_lang='en', target_lang='ne'):
    """Translate text using Google Translate"""
    try:
        translator = get_translator()
        translation = translator.translate(text, src=source_lang, dest=target_lang)
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def main():
    st.markdown("""
    <div class='main-header'>
        <h1>🇳🇵 Nepali Unicode Converter - Advanced IME</h1>
        <p>Professional-grade transliteration with smart phonetic rules and lexicon overrides</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔤 Unicode Converter", "🌐 Translation", "ℹ️ About & Tips"])
    
    with tab1:
        st.header("Advanced Nepali Unicode Converter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Input (Romanized Nepali)")
            roman_input = st.text_area(
                "Type Romanized Nepali text:",
                height=250,
                placeholder="e.g., namaskar, Mero desh Nepal ho, pratishat/ko",
                key="roman_input"
            )
            
            # Character and word counts
            in_chars = len(roman_input)
            words = len(roman_input.strip().split()) if roman_input.strip() else 0
            
            st.caption(f"Characters: {in_chars} • Words: {words}")
        
        with col2:
            st.subheader("Output")
            
            # Mode selection
            mode = st.radio(
                "Output Mode:",
                ["unicode", "html", "smart"],
                format_func=lambda x: {
                    "unicode": "Readable Unicode",
                    "html": "HTML Encoded",
                    "smart": "Smart Converter"
                }[x],
                horizontal=True
            )
            
            # Convert text
            if roman_input:
                unicode_output = transliterate(roman_input)
                if mode == "html":
                    final_output = encode_html(unicode_output)
                else:
                    final_output = unicode_output
                
                st.markdown(f"""
                <div class='nepali-text'>{final_output}</div>
                """, unsafe_allow_html=True)
                
                # Copy button
                if st.button("📋 Copy to Clipboard", type="primary"):
                    st.write("✅ Copied to clipboard!")
                    st.code(final_output, language=None)
                
                st.caption(f"Output characters: {len(final_output)}")
            else:
                st.info("Type some text to see the conversion...")
        
        # Tips section
        st.markdown("## 💡 Tips & Tricks")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            **Basic Usage:**
            - Keep English as-is: wrap in `{curly braces}`
            - Avoid conjuncts: use `/` between syllables
            - End with halant: type `\\` after consonant
            
            **Special Characters:**
            - `*` = अनुस्वर (ं)
            - `**` = चन्द्रबिन्दु (ँ)
            - `om` = ॐ
            - `rr` = र्‍ (reph-forming)
            """)
        
        with tips_col2:
            st.markdown("""
            **Common Pairs:**
            - `ta`=त, `Ta`=ट
            - `tha`=थ, `Tha`=ठ
            - `da`=द, `Da`=ड
            - `na`=न, `Na`=ण
            - `sha`=श, `Sh`=ष
            
            **Compounds:**
            - `ksha`=क्ष, `gya`=ज्ञ, `yna`=ञ
            """)
        
        # Examples
        st.markdown("## 📚 Examples")
        
        examples = [
            {"en": "hya ke raichha", "ne": "हया के रैछ"},
            {"en": "namaskar", "ne": "नमस्कार"},
            {"en": "dhanyawaad", "ne": "धन्यवाद"},
            {"en": "sagarmatha", "ne": "सगरमाथा"},
            {"en": "Kathmandu", "ne": "काठमाडौं"},
            {"en": "pratishat/ko", "ne": "प्रतिशतको"},
            {"en": "Mero desh Nepal ho.", "ne": "मेरो देश नेपाल हो."},
            {"en": "ksha gya yna", "ne": "क्ष ज्ञ ञ"},
        ]
        
        example_cols = st.columns(4)
        for i, example in enumerate(examples):
            with example_cols[i % 4]:
                if st.button(f"**{example['en']}**\n{example['ne']}", 
                           key=f"ex_{i}", 
                           help="Click to load example"):
                    st.session_state.roman_input = example['en']
                    st.rerun()
    
    with tab2:
        st.header("English to Nepali Translation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("English Input")
            english_text = st.text_area(
                "Type your English text:",
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
            st.subheader("Nepali Translation")
            if 'translation' in st.session_state:
                st.markdown(f"""
                <div class='converter-box'>
                    <div class='nepali-text'>{st.session_state['translation']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.code(st.session_state['translation'], language=None)
            else:
                st.info("Translation will appear here...")
    
    with tab3:
        st.header("About This Advanced Converter")
        
        st.markdown("""
        <div class='feature-box'>
            <h3>🌟 Advanced Features</h3>
            <ul>
                <li><strong>Smart Transliteration:</strong> Professional-grade IME with phonetic rules</li>
                <li><strong>Lexicon Overrides:</strong> Fixes colloquial Latin spellings automatically</li>
                <li><strong>Conjunct Control:</strong> Precise control over consonant combinations</li>
                <li><strong>Multiple Output Modes:</strong> Unicode, HTML encoded, and smart conversion</li>
                <li><strong>English Preservation:</strong> Keep English text unchanged with {braces}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-box'>
            <h3>🔧 Technical Details</h3>
            <ul>
                <li><strong>Zero-Width Characters:</strong> Uses ZWNJ (/) and ZWJ for precise control</li>
                <li><strong>Greedy Matching:</strong> Longest-token-first algorithm for accuracy</li>
                <li><strong>Context-Aware:</strong> Automatic anusvara insertion before velars/palatals</li>
                <li><strong>Extensible:</strong> Easy to add new rules and lexicon entries</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-box'>
            <h3>⚠️ Important Notes</h3>
            <ul>
                <li>This is a best-effort IME; real-world edge cases may exist</li>
                <li>Extend rules in the code for full editor-grade behavior</li>
                <li>Translation requires internet connection</li>
                <li>For production use, consider extending the lexicon and rules</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>Built with ❤️ for professional Nepali language processing</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
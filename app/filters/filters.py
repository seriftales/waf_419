#Filtreleme işlemleri
# Bu modül gelen istekleri filtreler

import re
from app.config import KEYWORDS
from app.utils.logger import logger
from urllib.parse import parse_qs

#WAF kural motoru
class Rules:
    def __init__(self):
        self.blocked_patterns = []
        self.load_patterns()

    def load_patterns(self):
        #JSON dosyasındaki kuralları okur ve performansı artırmak için Regex objesi olarak derler.
        for rule_category, rules in KEYWORDS.items():
            for rule in rules:
                if isinstance(rule, dict) and "pattern" in rule:
                    self.blocked_patterns.append({
                        "regex": re.compile(rule["pattern"], re.IGNORECASE),
                        "category": rule_category,  
                        "level": rule["level"],
                        "target": rule["target"]
                    })

    def check_pattern(self, text: str) -> bool:
        #Gelen metin üzerinde regex kurallarını kontrol eder.
        if not text:
            return False
        for rule in self.blocked_patterns:
            if rule["regex"].search(text):
                return True
        return False
    
    def is_blocked(self, path: str, body_bytes: bytes, query: str) -> bool:
        # 1. URL Path Kontrolü
        if self.check_pattern(path):
            return True
        
        # 2. Query String Kontrolü (HPP Zafiyeti v[0] yerine tam liste ile kapatıldı)
        if query: 
            parsed_query = parse_qs(query)
            query_string = ' '.join([f"{k}={val}" for k, v in parsed_query.items() for val in v])
            if self.check_pattern(query_string):
                return True

        # 3. HTTP Body Kontrolü (Görüntü/Binary yüklemelerinde çökmeyi engelleme)
        if body_bytes:
            try:
                # Hatalı/Binary karakterleri yoksayarak güvenli decode et
                body_text = body_bytes.decode('utf-8', errors='ignore')
                if self.check_pattern(body_text):
                    return True
            except Exception:
                pass # Payload metin değilse (örn: zip, png) tarama yapma

        return False
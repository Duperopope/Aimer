#!/usr/bin/env python3
"""
AIMER PRO - Test Rapide Webcam ✨
Version très simple pour test immédiat
"""

import cv2
import time

def test_webcam_details():
    """Test détaillé de webcam avec feedback utilisateur"""
    print("📹 TEST WEBCAM AIMER PRO")
    print("=" * 40)
    
    # Test de différents indices
    webcam_found = False
    
    for index in [0, 1, 2]:
        print(f"\n🔍 Test index {index}...")
        
        try:
            cap = cv2.VideoCapture(index)
            
            if cap.isOpened():
                print(f"  ✅ Index {index}: Webcam s'ouvre")
                
                # Test de lecture
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"  ✅ Index {index}: Lecture OK - {width}x{height}")
                    
                    # Test de 5 frames
                    print(f"  🎬 Test de 5 frames...")
                    success_count = 0
                    
                    for i in range(5):
                        ret, frame = cap.read()
                        if ret:
                            success_count += 1
                        time.sleep(0.1)
                    
                    print(f"  📊 Résultat: {success_count}/5 frames réussies")
                    
                    if success_count >= 3:
                        print(f"  🎉 WEBCAM FONCTIONNELLE sur index {index} !")
                        webcam_found = True
                        cap.release()
                        break
                    else:
                        print(f"  ⚠️  Index {index}: Trop d'échecs de lecture")
                
                else:
                    print(f"  ❌ Index {index}: Webcam s'ouvre mais ne lit pas")
                
                cap.release()
            else:
                print(f"  ❌ Index {index}: Webcam ne s'ouvre pas")
                
        except Exception as e:
            print(f"  💥 Index {index}: Erreur - {e}")
    
    print("\n" + "=" * 40)
    
    if webcam_found:
        print("🎉 RÉSULTAT: WEBCAM FONCTIONNELLE !")
        print("✅ Votre webcam est compatible avec AIMER PRO")
        return True
    else:
        print("❌ RÉSULTAT: AUCUNE WEBCAM FONCTIONNELLE")
        print("⚠️  Vérifiez:")
        print("   - Webcam connectée et allumée")
        print("   - Pilotes installés")
        print("   - Aucune autre app n'utilise la webcam")
        return False

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🎯 AIMER PRO - TEST WEBCAM                   ║
║               Test rapide de compatibilité                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        result = test_webcam_details()
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║ STATUT FINAL: {'✅ WEBCAM OK' if result else '❌ WEBCAM PROBLÈME':<30}               ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        if result:
            print("\n🚀 Vous pouvez maintenant lancer AIMER PRO avec:")
            print("   python launch.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")

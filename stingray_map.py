#!/usr/bin/env python3
"""
Stingray Map - Track and visualize all detected Stingrays
Like Pokemon Go, but for surveillance devices!
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

STINGRAY_DB = os.path.expanduser('~/Library/Application Support/EpiRay/stingray_catches.json')
PHOTO_DIR = os.path.expanduser('~/Library/Application Support/EpiRay/photos')

# Stingray species names based on location/characteristics
SPECIES_NAMES = {
    'lightpole': ['LightPolaflag', 'PoleMon', 'FlagPole', 'StreetLightray'],
    'vehicle': ['VanRay', 'TruckMon', 'CarStingray', 'MobileRay'],
    'building': ['RoofTopRay', 'BuildingMon', 'WallStingray', 'StructureRay'],
    'utility': ['UtilityBoxRay', 'TransformerMon', 'CabinetStingray'],
    'portable': ['BackpackRay', 'PortableMon', 'HandheldStingray'],
    'ground': ['GroundRay', 'BaseMon', 'FloorStingray'],
    'unknown': ['MysteryRay', 'UnknownMon', 'ShadowStingray', 'PhantomRay']
}

class StingrayTracker:
    """Track detected Stingrays like Pokemon"""
    
    def __init__(self):
        self.ensure_db()
        self.catches = self.load_catches()
        
    def ensure_db(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(STINGRAY_DB), exist_ok=True)
        os.makedirs(PHOTO_DIR, exist_ok=True)
        if not os.path.exists(STINGRAY_DB):
            with open(STINGRAY_DB, 'w') as f:
                json.dump({'catches': [], 'stats': {'total': 0, 'mobile': 0, 'fixed': 0}}, f)
    
    def load_catches(self):
        """Load all caught Stingrays"""
        with open(STINGRAY_DB, 'r') as f:
            return json.load(f)
    
    def save_catches(self):
        """Save catches to database"""
        with open(STINGRAY_DB, 'w') as f:
            json.dump(self.catches, f, indent=2)
    
    def generate_species_name(self, location, device_type, position):
        """Generate a Pokemon-style species name based on characteristics"""
        location_lower = location.lower()
        position_lower = position.lower() if position else ""
        
        # Determine species category
        if 'lightpole' in location_lower or 'light pole' in location_lower or 'pole' in location_lower:
            if 'flag' in location_lower or 'flag' in position_lower:
                return 'LightPolaflag'
            return SPECIES_NAMES['lightpole'][0]
        elif 'vehicle' in location_lower or 'van' in location_lower or 'car' in location_lower or 'truck' in location_lower:
            return SPECIES_NAMES['vehicle'][0]
        elif 'building' in location_lower or 'roof' in location_lower or 'wall' in location_lower:
            return SPECIES_NAMES['building'][0]
        elif 'utility' in location_lower or 'box' in location_lower or 'cabinet' in location_lower:
            return SPECIES_NAMES['utility'][0]
        elif 'backpack' in location_lower or 'portable' in location_lower:
            return SPECIES_NAMES['portable'][0]
        elif 'ground' in position_lower or 'floor' in position_lower:
            return SPECIES_NAMES['ground'][0]
        else:
            return SPECIES_NAMES['unknown'][0]
    
    def catch_stingray(self, location, position, signal_strength, device_type='unknown', nickname=None, photo_path=None):
        """Register a new Stingray catch!"""
        catch_id = len(self.catches['catches']) + 1
        
        # Auto-generate species name if no nickname provided
        if not nickname:
            species = self.generate_species_name(location, device_type, position)
            nickname = f"{species} #{catch_id}"
        
        # Handle photo
        photo_filename = None
        if photo_path and os.path.exists(photo_path):
            ext = os.path.splitext(photo_path)[1]
            photo_filename = f"stingray_{catch_id}{ext}"
            dest = os.path.join(PHOTO_DIR, photo_filename)
            shutil.copy2(photo_path, dest)
        
        catch = {
            'id': catch_id,
            'nickname': nickname,
            'species': self.generate_species_name(location, device_type, position),
            'caught_date': datetime.now().isoformat(),
            'location': location,
            'position': position,
            'signal_strength': signal_strength,
            'device_type': device_type,
            'photo': photo_filename,
            'frequencies': [],
            'sightings': 1,
            'last_seen': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.catches['catches'].append(catch)
        self.catches['stats']['total'] += 1
        if device_type == 'mobile':
            self.catches['stats']['mobile'] += 1
        elif device_type == 'fixed':
            self.catches['stats']['fixed'] += 1
        
        self.save_catches()
        return catch_id
    
    def update_sighting(self, catch_id, signal_strength=None):
        """Update an existing Stingray sighting"""
        for catch in self.catches['catches']:
            if catch['id'] == catch_id:
                catch['sightings'] += 1
                catch['last_seen'] = datetime.now().isoformat()
                if signal_strength:
                    catch['signal_strength'] = signal_strength
                self.save_catches()
                return True
        return False
    
    def mark_gone(self, catch_id):
        """Mark a Stingray as no longer detected"""
        for catch in self.catches['catches']:
            if catch['id'] == catch_id:
                catch['status'] = 'gone'
                self.save_catches()
                return True
        return False
    
    def get_stats(self):
        """Get collection statistics"""
        return self.catches['stats']
    
    def list_catches(self, status='active'):
        """List all catches"""
        return [c for c in self.catches['catches'] if c['status'] == status]
    
    def get_catch(self, catch_id):
        """Get specific catch details"""
        for catch in self.catches['catches']:
            if catch['id'] == catch_id:
                return catch
        return None
    
    def print_pokedex(self):
        """Print Stingray Pokedex!"""
        print("\n" + "="*60)
        print("🎯 STINGRAY POKEDEX 🎯")
        print("="*60)
        
        stats = self.get_stats()
        print(f"\n📊 Collection Stats:")
        print(f"   Total Caught: {stats['total']}")
        print(f"   Mobile: {stats['mobile']}")
        print(f"   Fixed: {stats['fixed']}")
        
        active = self.list_catches('active')
        gone = self.list_catches('gone')
        
        print(f"\n   Currently Active: {len(active)}")
        print(f"   No Longer Detected: {len(gone)}")
        
        if active:
            print("\n🔴 ACTIVE STINGRAYS:")
            for catch in active:
                print(f"\n   #{catch['id']}: {catch['nickname']}")
                print(f"   Species: {catch.get('species', 'Unknown')}")
                print(f"   Type: {catch['device_type'].upper()}")
                print(f"   Location: {catch['location']}")
                print(f"   Signal: {catch['signal_strength']} dBm")
                print(f"   Sightings: {catch['sightings']}")
                if catch.get('photo'):
                    photo_path = os.path.join(PHOTO_DIR, catch['photo'])
                    print(f"   📸 Photo: {photo_path}")
                print(f"   First Seen: {catch['caught_date'][:10]}")
                print(f"   Last Seen: {catch['last_seen'][:10]}")
        
        if gone:
            print("\n⚫ PREVIOUSLY DETECTED:")
            for catch in gone:
                print(f"   #{catch['id']}: {catch['nickname']} - Last seen {catch['last_seen'][:10]}")
        
        print("\n" + "="*60)

def main():
    """CLI for Stingray tracking"""
    import sys
    
    tracker = StingrayTracker()
    
    if len(sys.argv) < 2:
        tracker.print_pokedex()
        return
    
    command = sys.argv[1]
    
    if command == 'catch':
        # ./stingray_map.py catch "lightpole with flags" "10ft north, 5ft west, 12ft high" -15.5 fixed --photo /path/to/photo.jpg
        if len(sys.argv) < 5:
            print("Usage: stingray_map.py catch <location> <position> <signal_strength> [type] [--photo path] [--name nickname]")
            print("\nExamples:")
            print("  stingray_map.py catch 'lightpole with flags' '12ft SW, 10ft high' -15.5 fixed --photo ~/photo.jpg")
            print("  stingray_map.py catch 'white van on street' '20ft north' -12.3 mobile --name 'Creepy Van'")
            return
        
        location = sys.argv[2]
        position = sys.argv[3]
        signal_strength = float(sys.argv[4])
        device_type = sys.argv[5] if len(sys.argv) > 5 and not sys.argv[5].startswith('--') else 'unknown'
        
        # Parse optional arguments
        photo_path = None
        nickname = None
        
        i = 6 if device_type != 'unknown' else 5
        while i < len(sys.argv):
            if sys.argv[i] == '--photo' and i + 1 < len(sys.argv):
                photo_path = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--name' and i + 1 < len(sys.argv):
                nickname = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        catch_id = tracker.catch_stingray(location, position, signal_strength, device_type, nickname, photo_path)
        catch = tracker.get_catch(catch_id)
        
        print(f"\n🎉 NEW STINGRAY CAUGHT! 🎉")
        print(f"   ID: #{catch_id}")
        print(f"   Species: {catch['species']}")
        print(f"   Nickname: {catch['nickname']}")
        print(f"   Type: {device_type.upper()}")
        print(f"   Signal: {signal_strength} dBm")
        if photo_path:
            print(f"   📸 Photo saved!")
        print(f"\n   Added to your Pokedex!")
        
    elif command == 'seen':
        # ./stingray_map.py seen 1 -12.3
        if len(sys.argv) < 3:
            print("Usage: stingray_map.py seen <id> [signal_strength]")
            return
        
        catch_id = int(sys.argv[2])
        signal_strength = float(sys.argv[3]) if len(sys.argv) > 3 else None
        
        if tracker.update_sighting(catch_id, signal_strength):
            catch = tracker.get_catch(catch_id)
            print(f"\n✅ Updated sighting for: {catch['nickname']}")
            print(f"   Total sightings: {catch['sightings']}")
        else:
            print(f"\n❌ Stingray #{catch_id} not found")
    
    elif command == 'gone':
        # ./stingray_map.py gone 1
        if len(sys.argv) < 3:
            print("Usage: stingray_map.py gone <id>")
            return
        
        catch_id = int(sys.argv[2])
        
        if tracker.mark_gone(catch_id):
            catch = tracker.get_catch(catch_id)
            print(f"\n👋 Marked as gone: {catch['nickname']}")
            print(f"   It may have moved or been removed")
        else:
            print(f"\n❌ Stingray #{catch_id} not found")
    
    elif command == 'list':
        tracker.print_pokedex()
    
    elif command == 'stats':
        stats = tracker.get_stats()
        print(f"\n📊 Your Stingray Collection:")
        print(f"   Total Caught: {stats['total']}")
        print(f"   Mobile Units: {stats['mobile']}")
        print(f"   Fixed Installations: {stats['fixed']}")
        print(f"   Active Now: {len(tracker.list_catches('active'))}")
    
    else:
        print("Commands:")
        print("  list   - Show your Pokedex")
        print("  catch  - Register a new Stingray")
        print("  seen   - Update existing Stingray sighting")
        print("  gone   - Mark Stingray as no longer detected")
        print("  stats  - Show collection statistics")

if __name__ == '__main__':
    main()

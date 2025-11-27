import json
import os
import time
import datetime
from infosec_banking.utils.colors import print_processing, print_success, print_error, print_warning, print_info
from infosec_banking.config import AUDIT_LOG_FILE

class StorageManager:
    @staticmethod
    @staticmethod
    def atomic_write_json(path: str, data):
        """Writes JSON atomically with backup and retry logic"""
        path_tmp = path + '.tmp'
        path_bak = path + '.bak'
        
        for attempt in range(3):
            try:
                # print_processing(f"Saving {os.path.basename(path)}...")
                # time.sleep(0.1) # Removed sleep to speed up
                
                with open(path_tmp, 'w') as f:
                    json.dump(data, f, indent=4)
                    f.flush()
                    os.fsync(f.fileno()) # Ensure write to disk
                
                if os.path.exists(path):
                    if os.path.exists(path_bak):
                        try:
                            os.remove(path_bak)
                        except OSError:
                            pass # Might be open, but we try to continue
                    
                    try:
                        os.replace(path, path_bak)
                    except OSError:
                        # Fallback if replace fails (e.g. cross-device)
                        if os.path.exists(path_bak):
                             os.remove(path_bak)
                        os.rename(path, path_bak)
                
                os.replace(path_tmp, path)
                print_success(f"Saved {os.path.basename(path)}")
                return # Success
                
            except Exception as e:
                print_warning(f"Save attempt {attempt+1} failed for {path}: {e}")
                time.sleep(0.2) # Wait a bit before retry
                if attempt == 2:
                    print_error(f"Failed to save {path} after 3 attempts: {e}")
                    if os.path.exists(path_tmp):
                        try:
                            os.remove(path_tmp)
                        except:
                            pass
                    raise

    @staticmethod
    def load_json(path: str, default_data=None):
        """Loads JSON with recovery from backup"""
        path_bak = path + '.bak'
        
        if os.path.exists(path):
            try:
                print_processing(f"Loading {os.path.basename(path)}...")
                time.sleep(0.1)
                with open(path, 'r') as f:
                    data = json.load(f)
                print_success(f"Loaded {os.path.basename(path)}")
                return data
            except (json.JSONDecodeError, IOError) as e:
                print_warning(f"Corrupted {path}. Attempting recovery...")
        
        if os.path.exists(path_bak):
            try:
                with open(path_bak, 'r') as f:
                    data = json.load(f)
                StorageManager.atomic_write_json(path, data)
                print_success(f"Recovered {path} from backup")
                return data
            except (json.JSONDecodeError, IOError) as e:
                print_error(f"Backup also corrupted: {e}")
        
        print_info(f"Initializing new {os.path.basename(path)}")
        return default_data if default_data is not None else {}

    @staticmethod
    def log_operation(user_id, action, status="SUCCESS"):
        """Writes to audit log"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] User: {user_id:<12} | Status: {status:<8} | Action: {action}\n"
        try:
            with open(AUDIT_LOG_FILE, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print_error(f"Could not write audit log: {e}")

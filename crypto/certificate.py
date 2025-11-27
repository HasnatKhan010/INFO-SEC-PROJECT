import json
import datetime

class Certificate:
    """Represents a Digital Certificate (X.509 style)"""
    
    def __init__(self, serial_number, subject, issuer, public_key, valid_from=None, valid_to=None, signature=None):
        self.serial_number = serial_number
        self.subject = subject  # User ID
        self.issuer = issuer    # CA Name
        self.public_key = public_key
        self.valid_from = valid_from if valid_from else datetime.datetime.now().isoformat()
        self.valid_to = valid_to if valid_to else (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
        self.signature = signature

    def to_dict(self):
        """Converts certificate to dictionary"""
        return {
            "serial_number": self.serial_number,
            "subject": self.subject,
            "issuer": self.issuer,
            "public_key": self.public_key,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "signature": self.signature
        }

    @staticmethod
    def from_dict(data):
        """Creates certificate from dictionary"""
        return Certificate(
            serial_number=data["serial_number"],
            subject=data["subject"],
            issuer=data["issuer"],
            public_key=data["public_key"],
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            signature=data.get("signature")
        )

    def get_data_to_sign(self):
        """Returns the canonical string representation of the certificate data for signing"""
        data = {
            "serial_number": self.serial_number,
            "subject": self.subject,
            "issuer": self.issuer,
            "public_key": self.public_key,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

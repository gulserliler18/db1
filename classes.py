from flask_login import UserMixin

class Citizen(UserMixin):
    def __init__(self, citizen_id, name, password, is_official):
        self.citizen_id = citizen_id
        self.name = name
        self.password = password
        self.is_official = is_official
        self.active = True

    def get_id(self):
        return self.citizen_id

    def get_is_official(self):
        return self.is_official

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True


class Building:
    def __init__(self, BuildingId, BC, ConstructorID, BIY, City, Nh, Str, Dist, TD, LR, Safety, Complaint):
        self.BuildingId = BuildingId
        self.BC = BC
        self.ConstructorID = ConstructorID
        self.BIY = BIY
        self.City = City
        self.Nh = Nh
        self.Str = Str
        self.Dist = Dist
        self.TD = TD
        self.LR = LR
        self.Safety = Safety
        self.Complaint = Complaint

cities = [
{"id":"15","name":"BURDUR"},
{"id":"26","name":"ESKİŞEHİR"},
{"id":"18","name":"ÇANKIRI"},
{"id":"80","name":"OSMANİYE"},
{"id":"41","name":"KOCAELİ"},
{"id":"27","name":"GAZİANTEP"},
{"id":"31","name":"HATAY"},
{"id":"38","name":"KAYSERİ"},
{"id":"29","name":"GÜMÜŞHANE"},
{"id":"54","name":"SAKARYA"},
{"id":"16","name":"BURSA"},
{"id":"69","name":"BAYBURT"},
{"id":"17","name":"ÇANAKKALE"},
{"id":"57","name":"SİNOP"},
{"id":"74","name":"BARTIN"},
{"id":"503","name":"MAĞUSA (KIBRIS)"},
{"id":"33","name":"MERSİN"},
{"id":"51","name":"NİĞDE"},
{"id":"42","name":"KONYA"},
{"id":"60","name":"TOKAT"},
{"id":"2","name":"ADIYAMAN"},
{"id":"6","name":"ANKARA"},
{"id":"66","name":"YOZGAT"},
{"id":"52","name":"ORDU"},
{"id":"53","name":"RİZE"},
{"id":"1","name":"ADANA"},
{"id":"40","name":"KIRŞEHİR"},
{"id":"76","name":"IĞDIR"},
{"id":"45","name":"MANİSA"},
{"id":"21","name":"DİYARBAKIR"},
{"id":"64","name":"UŞAK"},
{"id":"501","name":"LEFKOŞE (KIBRIS)"},
{"id":"5","name":"AMASYA"},
{"id":"24","name":"ERZİNCAN"},
{"id":"32","name":"ISPARTA"},
{"id":"502","name":"GİRNE (KIBRIS)"},
{"id":"23","name":"ELAZIĞ"},
{"id":"78","name":"KARABÜK"},
{"id":"30","name":"HAKKARİ"},
{"id":"36","name":"KARS"},
{"id":"67","name":"ZONGULDAK"},
{"id":"68","name":"AKSARAY"},
{"id":"44","name":"MALATYA"},
{"id":"10","name":"BALIKESİR"},
{"id":"20","name":"DENİZLİ"},
{"id":"49","name":"MUŞ"},
{"id":"73","name":"ŞIRNAK"},
{"id":"48","name":"MUĞLA"},
{"id":"59","name":"TEKİRDAĞ"},
{"id":"39","name":"KIRKLARELİ"},
{"id":"56","name":"SİİRT"},
{"id":"28","name":"GİRESUN"},
{"id":"63","name":"ŞANLIURFA"},
{"id":"9","name":"AYDIN"},
{"id":"72","name":"BATMAN"},
{"id":"13","name":"BİTLİS"},
{"id":"3","name":"AFYONKARAHİSAR"},
{"id":"8","name":"ARTVİN"},
{"id":"4","name":"AĞRI"},
{"id":"77","name":"YALOVA"},
{"id":"50","name":"NEVŞEHİR"},
{"id":"61","name":"TRABZON"},
{"id":"58","name":"SİVAS"},
{"id":"7","name":"ANTALYA"},
{"id":"37","name":"KASTAMONU"},
{"id":"47","name":"MARDİN"},
{"id":"46","name":"KAHRAMANMARAŞ"},
{"id":"25","name":"ERZURUM"},
{"id":"75","name":"ARDAHAN"},
{"id":"81","name":"DÜZCE"},
{"id":"55","name":"SAMSUN"},
{"id":"19","name":"ÇORUM"},
{"id":"65","name":"VAN"},
{"id":"14","name":"BOLU"},
{"id":"43","name":"KÜTAHYA"},
{"id":"11","name":"BİLECİK"},
{"id":"34","name":"İSTANBUL"},
{"id":"79","name":"KİLİS"},
{"id":"62","name":"TUNCELİ"},
{"id":"12","name":"BİNGÖL"},
{"id":"22","name":"EDİRNE"},
{"id":"71","name":"KIRIKKALE"},
{"id":"70","name":"KARAMAN"},
{"id":"35","name":"İZMİR"}
]
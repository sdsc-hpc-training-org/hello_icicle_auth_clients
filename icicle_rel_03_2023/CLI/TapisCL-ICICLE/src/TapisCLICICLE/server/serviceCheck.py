from tapipy.tapis import Tapis


class ServiceChecker:
    def __supports_systems(self):
        if self.t.systems.getSchedulerProfiles():
            return True
        return False

    def check_services(self):
        return {
            "SYSTEM SUPPORT":self.__supports_systems(),
            "FILES SUPPORT":self.__supports_systems(),
            "APPS AND JOBS SUPPORT":self.__supports_systems(),
            "PODS SUPPORT":True
        }
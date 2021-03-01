import copy
import json
import logging
from typing import List

from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.enum.RiskLevel import RiskLevel
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from src.main.psHandler.ProcessHandler import ProcessHandler


class Modeller:

    def __init__(self, logger_name: str = "Modeller") -> None:
        """
        Abstracts the daemon that models the collected process information.
        :param logger_name: The name of the logger.
        :type logger_name: str
        """
        self.__logger_name = logger_name
        self.__modelled_applications = list()  # Doesn't store non-running applications.

    @staticmethod
    def model_application_profiles(application_profiles: List[AppProfile]) -> List[AppSummary]:
        """
        Create the frequency model for a list of AppProfiles. This is the main method of this class.
        :param application_profiles: the application profiles to model.
        :type application_profiles: List[AppProfile]
        :return: the model of the provided application profiles.
        :rtype List[AppSummary]
        """
        frequency_technique = FrequencyTechnique()

        return frequency_technique(application_profiles)

    def get_modelled_applications(self) -> List[AppSummary]:
        """
        Gets the modelled applications.
        :return: The modelled applications.
        :rtype: List[AppSummary]
        """
        return copy.deepcopy(self.__modelled_applications)

    def get_abnormal_applications(self) -> List[AppSummary]:
        """
        Gets the list of abnormal applications.
        :return: The abnormal applications.
        :rtype: List[AppSummary]
        """
        abnormal_applications = list()
        for app_summary in self.__modelled_applications:

            app_risk_level = app_summary.get_risk_level()
            if app_risk_level is not RiskLevel.none:
                abnormal_applications.append(app_summary)
        return abnormal_applications

    def get_modelled_application_as_json(self) -> str:
        """
        Converts a list of modelled apps into a json object.
        It should be used for preparing data to send to connected clients.
        :return: The modelled apps as a json object.
        :rtype: str
        """
        modelled_apps_dict = [str(modelled_app) for modelled_app in self.__modelled_applications]
        return json.dumps(modelled_apps_dict)

    def model_running_applications(self) -> None:
        """
        Models running applications.
        """
        logger = logging.getLogger(self.__logger_name)
        modelled_apps = list()

        saved_application_profile_names = AppProfileDataManager.get_saved_app_profiles_names()
        logger.info("Starting to model running applications.")

        for saved_app_profile_name in saved_application_profile_names:
            app_profile = AppProfileDataManager.get_saved_profile(saved_app_profile_name)
            if ProcessHandler.is_application_recently_retrieved(app_profile):
                modelled_app = Modeller.model_application_profiles([app_profile])
                modelled_apps.extend(modelled_app)

        self.__modelled_applications = modelled_apps
        logger.info("Finished modelling {} application profiles.".format(len(modelled_apps)))
        # Save data
        abnormal_applications = self.get_abnormal_applications()
        AppProfileDataManager.save_abnormal_apps(abnormal_applications)

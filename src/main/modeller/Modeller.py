import copy
import logging
from typing import List

from paths import LOGGER_DIR_PATH, LOGGER_TEST_DIR_PATH
from src.main.common.AppProfile import AppProfile
from src.main.common.AppSummary import AppSummary
from src.main.common.Daemon import Daemon
from src.main.common.LoggerUtils import LoggerUtils
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.main.psHandler.AppProfileDataManager import AppProfileDataManager
from wades_config import log_file_extension


class Modeller(Daemon):

    def __init__(self, logger_name: str = "Modeller", is_test: bool = False) -> None:
        """
        Abstracts the daemon that models the collected process information.
        :param logger_name: The name of the logger.
        :type logger_name: str
        :param is_test: Flag for checking if this is called by a test. It changes the log path according to the value.
        :type is_test: bool
        """
        logger_base_dir = LOGGER_DIR_PATH if not is_test else LOGGER_TEST_DIR_PATH
        LoggerUtils.setup_logger(logger_name, logger_base_dir / (logger_name + log_file_extension))
        self.__logger = logging.getLogger(logger_name)
        self.__modelled_applications = list()
        super(Modeller, self).__init__(self.__logger, logger_name)

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

    def run(self) -> None:
        """
        Starts the modeller as a daemon. This method overrides the method in the parent class.
        """
        while True:
            application_profiles = AppProfileDataManager.get_saved_profiles()
            self.__logger.info("Starting to model {} application profiles.".format(len(application_profiles)))
            Modeller.model_application_profiles(application_profiles)
            self.__logger.info("Finished modelling {} application profiles.".format(len(application_profiles)))

    def get_modelled_applications(self) -> List[AppSummary]:
        """
        Gets the modelled applications.
        :return: The modelled applications.
        :rtype: List[AppSummary]
        """
        return copy.deepcopy(self.__modelled_applications)

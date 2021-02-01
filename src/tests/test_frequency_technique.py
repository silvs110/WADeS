from collections import namedtuple
from typing import Dict

import pytest

from src.main.common.enum.AppProfileAttribute import AppProfileAttribute
from src.main.common.enum.AppSummaryAttribute import AppSummaryAttribute
from src.main.common.enum.RiskLevel import RiskLevel
from wades_config import anomaly_detected_message
from src.main.modeller.FrequencyTechnique import FrequencyTechnique
from src.tests.test_helpers import build_application_profile_list

"""
This file contains test for FrequencyTechnique class.
Methods with functional tests:
* __init__()
* __call__()
* set_minimum_count_non_anomalous()
* get_minimum_count_non_anomalous()

Input validation test:
* __init__()
* __call__()
* set_minimum_count_non_anomalous()

"""

AppModellingTestScenario = namedtuple("AppModellingTestScenario", 'app_name, risk_level, anomalous_attrs, is_anomalous')


# noinspection PyTypeChecker
def test_create_frequency_technique_instance_with_invalid_inputs() -> None:
    """
    Test create the instance of frequency technique with invalid inputs.
    :return:
    """
    with pytest.raises(TypeError):
        FrequencyTechnique(min_number_count_non_anomalous=None)
    with pytest.raises(TypeError):
        FrequencyTechnique(min_number_count_non_anomalous="Something random")
    with pytest.raises(ValueError):
        FrequencyTechnique(min_number_count_non_anomalous=-2)


def test_set_min_number_count_non_anomalous_with_valid_inputs() -> None:
    """
    Test set the minimum_count_non_anomalous with valid values.
    """
    fq = FrequencyTechnique()

    new_min_number_count_non_anomalous_value = 2

    min_number_count_non_anomalous = fq.get_minimum_count_non_anomalous()
    assert min_number_count_non_anomalous == 5  # Default value is 5
    fq.set_minimum_count_non_anomalous(new_value=2)
    min_number_count_non_anomalous = fq.get_minimum_count_non_anomalous()
    assert new_min_number_count_non_anomalous_value == min_number_count_non_anomalous


# noinspection PyTypeChecker
def test_set_min_number_count_non_anomalous_with_invalid_inputs() -> None:
    """
    Test set the minimum_count_non_anomalous value with invalid inputs.
    """
    fq = FrequencyTechnique()

    with pytest.raises(TypeError):
        fq.set_minimum_count_non_anomalous(new_value=None)

    with pytest.raises(TypeError):
        fq.set_minimum_count_non_anomalous(new_value="Some random value")

    with pytest.raises(ValueError):
        fq.set_minimum_count_non_anomalous(new_value=-1)


# noinspection PyTypeChecker
def test_execute_frequency_modelling_with_invalid_inputs() -> None:
    """
    Test modelling the frequency technique with invalid inputs.
    """
    fq = FrequencyTechnique()
    # Invalid collection
    with pytest.raises(TypeError):
        fq(data=None)

    # Invalid collection as input
    with pytest.raises(TypeError):
        fq(data=dict())

    # List of invalid list
    data = [1, 2]
    with pytest.raises(TypeError):
        fq(data=data)


@pytest.mark.parametrize("modelling_test_scenario",
                         [
                             AppModellingTestScenario("common_case_app", RiskLevel.none, set(), False),
                             AppModellingTestScenario("non_anomalous_app", RiskLevel.none, set(), False),
                             AppModellingTestScenario("app_with_anomalous_very_high_memory_usage", RiskLevel.high,
                                                      {AppProfileAttribute.memory_infos.name}, True),
                             AppModellingTestScenario("app_with_anomalous_high_memory_usage", RiskLevel.medium,
                                                      {AppProfileAttribute.memory_infos.name}, True),
                             AppModellingTestScenario("app_with_anomalous_very_low_memory_usage", RiskLevel.medium,
                                                      {AppProfileAttribute.memory_infos.name}, True),
                             AppModellingTestScenario("app_with_anomalous_low_memory_usage", RiskLevel.low,
                                                      {AppProfileAttribute.memory_infos.name}, True),
                             AppModellingTestScenario("app_with_anomalous_unknown_user", RiskLevel.medium,
                                                      {AppProfileAttribute.usernames.name}, True),
                             AppModellingTestScenario("app_with_anomalous_unknown_opened_file_whitelist",
                                                      RiskLevel.medium, {AppProfileAttribute.opened_files.name}, True),
                             AppModellingTestScenario("app_with_blacklisted_file",
                                                      RiskLevel.high, {AppProfileAttribute.opened_files.name}, True),
                             AppModellingTestScenario("app_with_high_risk_and_low_risk_anomaly",
                                                      RiskLevel.high, {AppProfileAttribute.memory_infos.name,
                                                                       AppProfileAttribute.opened_files.name}, True),
                             AppModellingTestScenario("app_with_abnormal_memory_usage",
                                                      RiskLevel.medium, {AppProfileAttribute.memory_infos.name}, True)
                         ]
                         )
def test_execute_frequency_modelling_with_anomalies(saved_test_app_profiles_dict: Dict[str, dict],
                                                    modelling_test_scenario: AppModellingTestScenario) -> None:
    """
    Test modelling the application profiles using the frequency technique.
    :param saved_test_app_profiles_dict: The retrieved test application profiles.
    :type saved_test_app_profiles_dict: Dict[str, dict]
    :param modelling_test_scenario: The modelling test scenarios.
    :type modelling_test_scenario: AppModellingTestScenario
    """
    app_profiles = build_application_profile_list(app_profiles_dict=saved_test_app_profiles_dict,
                                                  application_names={modelling_test_scenario.app_name})
    fq = FrequencyTechnique(is_test=True)
    app_summaries = fq(data=app_profiles)

    assert len(app_summaries) == 1
    app_summary = app_summaries[0]
    app_summary_dict = app_summary.dict_format()

    if modelling_test_scenario.is_anomalous:
        assert app_summary_dict[AppSummaryAttribute.error_message.name] == anomaly_detected_message
    else:
        assert app_summary_dict[AppSummaryAttribute.error_message.name] is None
    assert app_summary_dict[AppSummaryAttribute.risk.name] == modelling_test_scenario.risk_level
    assert app_summary_dict[AppSummaryAttribute.abnormal_attributes.name] == modelling_test_scenario.anomalous_attrs

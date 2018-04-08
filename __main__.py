import sys
import logging

from ArgumentProcessingService import ArgumentProcessingService
from MachineLearningService import MachineLearningService
from Utilities.SafeCastUtil import SafeCastUtil
from Utilities.FileConverter import FileConverter

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.INFO)


def main():
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        promptUserForInput()
    elif len(arguments) == 1:
        first_argument = arguments[0]
        if first_argument.lower().endswith(".mat"):
            FileConverter.convertMatLabToCSV(first_argument)
        else:
            runMainCellLineAnalysis(first_argument)
    return


def promptUserForInput():
    simulation_to_run = input("-------Main Menu-------\n"
                              "Choose your task:\n"
                              "\t0: Analysis of cell lines\n"
                              "\t1: Convert MATLAB to CSV file\n"  
                              "\tQ: Quit\n")

    option_as_int = SafeCastUtil.safeCast(simulation_to_run, int)
    option_as_string = SafeCastUtil.safeCast(simulation_to_run, str, "Q")

    if option_as_string == "Q":
        return
    elif option_as_int == 0:
        input_folder = recursivelyPromptUser("Enter path of input folder:\n", str)
        runMainCellLineAnalysis(input_folder)
    elif option_as_int == 1:
        matlab_file = recursivelyPromptUser("Enter path of .mat file:\n", str)
        FileConverter.convertMatLabToCSV(matlab_file)


def runMainCellLineAnalysis(input_folder):
    valid_inputs = handleInputFolderProcessing(input_folder)
    if valid_inputs is not None:
        performMachineLearning(valid_inputs, input_folder)


def recursivelyPromptUser(message, return_type):
    response = input(message)
    cast_response = SafeCastUtil.safeCast(response, return_type)
    if cast_response is None:
        print("Invalid command, looking for an input of type %.\n", return_type)
        recursivelyPromptUser(message, return_type)
    else:
        return response


def handleInputFolderProcessing(input_folder):
    argument_processing_service = ArgumentProcessingService(input_folder)
    full_inputs = argument_processing_service.handleInputFolder()
    if not full_inputs:
        log.error("Exiting program, invalid data sent in target folder.")
        return None
    return full_inputs


def performMachineLearning(valid_inputs, input_folder):
    machine_learning_service = MachineLearningService(valid_inputs)
    machine_learning_service.analyze(input_folder)


if __name__ == "__main__":
    main()

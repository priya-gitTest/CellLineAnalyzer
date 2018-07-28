import numpy as np
import random
import csv

from Utilities.SafeCastUtil import SafeCastUtil
from ArgumentProcessingService import ArgumentProcessingService


class RandomizedDataGenerator(object):

    GENERATED_DATA_FOLDER = "AutoGeneratedDataFolder"

    FEATURE_PREFIX = "feature"
    SIGNIFICANT_FEATURE_PREFIX = "significant_feature"

    SIGNIFICANT_GENE_LIST = "significant_gene_list"

    CATEGORICAL_SUFFIX = "cat"
    INTEGER_SUFFIX = "int"
    FLOAT_SUFFIX = "float"

    PCT_CATEGORICAL = .1


    @staticmethod
    def generateRandomizedFiles(num_feature_files, num_cells, num_features, is_classifier, monte_carlo_permutations,
                                data_split, individual_algorithm=None, individual_hyperparams=None):
        features_per_file = SafeCastUtil.safeCast(num_features / num_feature_files, int)
        results = RandomizedDataGenerator.generateResultsCSV(is_classifier, num_cells)
        important_features = random.sample(range(1, features_per_file + 1),
                                           SafeCastUtil.safeCast((features_per_file / 3), int))

        file_names = RandomizedDataGenerator.generateFeaturesCSVs(num_feature_files, num_cells, features_per_file,
                                                                  results, important_features)
        RandomizedDataGenerator.generateGeneLists(features_per_file, important_features)
        RandomizedDataGenerator.generateArgsTxt(is_classifier, monte_carlo_permutations, data_split,
                                                individual_algorithm, file_names[0], individual_hyperparams)
        return

    @staticmethod
    def generateResultsCSV(is_classifier, num_cells):
        results = []
        with open(RandomizedDataGenerator.GENERATED_DATA_FOLDER + "/" + ArgumentProcessingService.RESULTS + ".csv",
                  'w', newline='') as results_file:
            writer = csv.writer(results_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["cell_line_name"] + ["result"])
            for cell in range(0, num_cells):
                cell_name = "cell_line" + SafeCastUtil.safeCast(cell, str)
                if is_classifier:
                    result = np.random.randint(0, 2)
                    writer.writerow([cell_name, result])
                else:
                    result = np.random.random_sample()
                    writer.writerow([cell_name, result])
                results.append(result)
        return results

    @staticmethod
    def generateFeaturesCSVs(num_feature_files, num_cells, features_per_file, results, important_features):
        features = []

        for feature in range(1, features_per_file + 1):
            features.append(RandomizedDataGenerator.FEATURE_PREFIX + SafeCastUtil.safeCast(feature, str))
        for significant_feature in range(1, SafeCastUtil.safeCast(features_per_file / 10, int) + 1):
            features.append(RandomizedDataGenerator.SIGNIFICANT_FEATURE_PREFIX +
                            SafeCastUtil.safeCast(significant_feature, str))

        file_names = []
        for file_num in range(1, num_feature_files + 1):
            file_name = RandomizedDataGenerator.determineFileName(file_num)
            file_names.append(file_name.split("/")[1].split(".csv")[0])
            with open(file_name, 'w', newline='') as feature_file:
                writer = csv.writer(feature_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                features_in_this_file = []
                for i in range(0, len(features)):
                    if not i in important_features or random.random() > 0.5:
                        features_in_this_file.append(features[i])
                writer.writerow(features_in_this_file)

                for cell in range(0, num_cells):
                    line = []
                    for feature in features_in_this_file:
                        if RandomizedDataGenerator.SIGNIFICANT_FEATURE_PREFIX in feature:
                            line += RandomizedDataGenerator.writeSignificantFeature(file_name, results[cell], feature)
                        else:
                            line += RandomizedDataGenerator.writeRandomFeature(file_name)
                    writer.writerow(line)
        return file_names

    @staticmethod
    def determineFileName(file_num):
        file_name = RandomizedDataGenerator.GENERATED_DATA_FOLDER + "/features_" + SafeCastUtil.safeCast(file_num, str)
        rand = np.random.random_sample()
        if rand < RandomizedDataGenerator.PCT_CATEGORICAL or file_num == 1:  # always have at least one categorical file
            file_name += RandomizedDataGenerator.CATEGORICAL_SUFFIX + ".csv"
        elif RandomizedDataGenerator.PCT_CATEGORICAL <= rand < \
                (RandomizedDataGenerator.PCT_CATEGORICAL + (1 - RandomizedDataGenerator.PCT_CATEGORICAL) / 2):
            file_name += RandomizedDataGenerator.INTEGER_SUFFIX + ".csv"
        else:
            file_name += RandomizedDataGenerator.FLOAT_SUFFIX + ".csv"
        return file_name

    @staticmethod
    def writeSignificantFeature(file_name, result, feature):
        feature_num = SafeCastUtil.safeCast(feature.split(RandomizedDataGenerator.SIGNIFICANT_FEATURE_PREFIX)[1], int)
        is_exponential = feature_num % 2 == 0
        if RandomizedDataGenerator.CATEGORICAL_SUFFIX in file_name:
            if result < 0.5:
                return [np.random.choice(["a", "b"])]
            return [np.random.choice(["c", "d"])]
        elif RandomizedDataGenerator.INTEGER_SUFFIX in file_name:
            if is_exponential:
                return [SafeCastUtil.safeCast((result * 100)**(2 * feature_num), int)]
            return [SafeCastUtil.safeCast(result * 10, int)]
        else:
            if is_exponential:
                return [result**(2 * feature_num)]
            return [result * 10]

    @staticmethod
    def writeRandomFeature(file_name):
        if RandomizedDataGenerator.CATEGORICAL_SUFFIX in file_name:
            return [SafeCastUtil.safeCast(np.random.choice(["a", "b", "c", "d", "e"]), str)]
        elif RandomizedDataGenerator.INTEGER_SUFFIX in file_name:
            return [SafeCastUtil.safeCast(np.random.randint(0, 100), str)]
        else:
            return [SafeCastUtil.safeCast(np.random.random_sample(), str)]

    @staticmethod
    def generateGeneLists(features_per_file, important_features):
        gene_list_num = 1
        while len(important_features) > 1:
            gene_list_size = random.randint(2, len(important_features))
            gene_list = [RandomizedDataGenerator.FEATURE_PREFIX + SafeCastUtil.safeCast(feature, str) for feature in
                         important_features[:gene_list_size]]
            important_features = important_features[gene_list_size:]
            file_name = RandomizedDataGenerator.GENERATED_DATA_FOLDER + "/" + ArgumentProcessingService.GENE_LISTS +\
                        SafeCastUtil.safeCast(gene_list_num, str) + ".csv"
            with open(file_name, "w") as file:
                writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(gene_list)
            gene_list_num += 1

        with open(RandomizedDataGenerator.GENERATED_DATA_FOLDER + "/" + RandomizedDataGenerator.SIGNIFICANT_GENE_LIST +
                  ".csv", "w") as file:
            writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            significant_features = []
            for significant_feature in range(1, SafeCastUtil.safeCast(features_per_file / 10, int) + 1):
                significant_features.append(RandomizedDataGenerator.SIGNIFICANT_FEATURE_PREFIX +
                                            SafeCastUtil.safeCast(significant_feature, str))
            gene_list = significant_features
            writer.writerow(gene_list)

    @staticmethod
    def generateArgsTxt(is_classifier, monte_carlo_permutations=10, data_split=.8,
                        individual_algorithm=None, important_features=None, individual_hyperparams=None):
        file_name = RandomizedDataGenerator.GENERATED_DATA_FOLDER + "/" + ArgumentProcessingService.ARGUMENTS_FILE
        args_file = open(file_name, 'w')
        classifier = '0'
        if is_classifier:
            classifier = '1'
        args_file.write('results=results.csv\n'
                        'is_classifier=' + classifier + "\n"
                        'inner_monte_carlo_permutations=' + SafeCastUtil.safeCast(monte_carlo_permutations, str) + '\n'
                        'outer_monte_carlo_permutations=' + SafeCastUtil.safeCast(monte_carlo_permutations, str) + '\n'
                        'data_split=' + SafeCastUtil.safeCast(data_split, str) + '\n'
                        'record_diagnostics=True\n' +
                        'binary_categorical_matrix=features_1cat.csv\n')
        if individual_algorithm is not None and important_features is not None:
            args_file.write('individual_train_algorithm=' + individual_algorithm + '\n'
                            'individual_train_combo=' + important_features + ":" +
                            RandomizedDataGenerator.SIGNIFICANT_GENE_LIST + '\n')
            if individual_hyperparams is not None:
                args_file.write('individual_train_hyperparams=' + individual_hyperparams + '\n')
        args_file.close()

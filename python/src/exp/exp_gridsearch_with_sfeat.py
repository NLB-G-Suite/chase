import sys

from exp.classifier_traintest_main import ChaseClassifier
from ml.vectorizer import fv_davison


def create_settings(sys_out, data_train, data_test):
    #sys_out='../../../output' #where the system will save its required files, such as the trained models
    #data_in='../../../data/labeled_data.csv'
    #data_in='/home/zqz/Work/hate-speech-and-offensive-language/data/labeled_data_small.csv'

    #setting this to true will perform param tuning on the training data,
    #will take significantly longer time. but possibly better results

    settings=[]
    settings.append(['td-tdf-jsf', #task name to identify model files
                     'td-tdf-jsf', #identifier to identify scores
                     data_train,
                     data_test,
                     fv_davison.FeatureVectorizerDavidson(),#what feature vectorizer to use
                     99, #fs option
                     sys_out])


    # settings.append(['tdo-scaling-gs', #task name to identify model files
    #                  'tdo-scaling-gs', #identifier to identify scores
    #                  data_in,
    #                  fv_davison.FeatureVectorizerDavidson(),#what feature vectorizer to use
    #                  False, #use feature selection, ONLY VALID FOR TRAINING
    #                  True, #do grid search for classifier params
    #                  -1, #use pca for dimensionality reduction
    #                  False, #grid search on pca
    #                  sys_out])
    return settings


settings = create_settings(sys.argv[1], sys.argv[2], sys.argv[3])
for ds in settings:
    print("##########\nSTARTING EXPERIMENT SETTING:" + '; '.join(map(str, ds)))
    classifier = ChaseClassifier(ds[0],  # task
                                     ds[1],  # identifier
                                     ds[2],  # data train
                                     ds[3],  # data test
                                     ds[4],  # fv
                                     ds[5],  # fs option
                                     ds[6]  # outfolder
                                     )
    classifier.gridsearch_with_selectedfeatures(True,
                                                "/home/zqz/Work/chase/output/models/td-tdf/svml-td-tdf-kb.m.features.csv",
                                                "/home/zqz/Work/chase/output/models/td-tdf/svml-td-tdf-sfm.m.features.csv",
                                                "/home/zqz/Work/chase/output/models/td-tdf/svml-td-tdf-rfe.m.features.csv")

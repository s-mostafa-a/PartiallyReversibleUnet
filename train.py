import comet_ml
import torch
import bratsDataset
import segmenter
import systemsetup

import experiments.noNewReversible as expConfig
#import experiments.noNewReversibleFat as expConfig
#import experiments.noNewNet as expConfig

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

def main(tds, vds):

    # setup experiment logging to comet.ml
    if expConfig.LOG_COMETML:
        hyper_params = {"experimentName": expConfig.EXPERIMENT_NAME,
                        "epochs": expConfig.EPOCHS,
                        "batchSize": expConfig.BATCH_SIZE,
                        "channels": expConfig.CHANNELS,
                        "virualBatchsize": expConfig.VIRTUAL_BATCHSIZE}
        expConfig.experiment.log_parameters(hyper_params)
        expConfig.experiment.add_tags([expConfig.EXPERIMENT_NAME, "ID{}".format(expConfig.id)])
        if hasattr(expConfig, "EXPERIMENT_TAGS"): expConfig.experiment.add_tags(expConfig.EXPERIMENT_TAGS)
        print(bcolors.OKGREEN + "Logging to comet.ml" + bcolors.ENDC)
    else:
        print(bcolors.WARNING + "Not logging to comet.ml" + bcolors.ENDC)

    # log parameter count
    if expConfig.LOG_PARAMCOUNT:
        paramCount = sum(p.numel() for p in expConfig.net.parameters() if p.requires_grad)
        print("Parameters: {:,}".format(paramCount).replace(",", "'"))

    #load data
    randomCrop = expConfig.RANDOM_CROP if hasattr(expConfig, "RANDOM_CROP") else None
    trainloader = torch.utils.data.DataLoader(tds, batch_size=expConfig.BATCH_SIZE, shuffle=True, pin_memory=True, num_workers=expConfig.DATASET_WORKERS)

    valloader = torch.utils.data.DataLoader(vds, batch_size=1, shuffle=False, pin_memory=True, num_workers=expConfig.DATASET_WORKERS)

    challengeValloader = torch.utils.data.DataLoader(vds, batch_size=1, shuffle=False, pin_memory=True, num_workers=expConfig.DATASET_WORKERS)

    seg = segmenter.Segmenter(expConfig, trainloader, valloader, challengeValloader)
    if hasattr(expConfig, "VALIDATE_ALL") and expConfig.VALIDATE_ALL:
        seg.validateAllCheckpoints()
    elif hasattr(expConfig, "PREDICT") and expConfig.PREDICT:
        seg.makePredictions()
    else:
        seg.train()

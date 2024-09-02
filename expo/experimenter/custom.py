from expo.experimenter import Experimenter
from expo.MCTS import create_initial_state
from expo.evaluation.evaluation import evaluate_score
import pandas as pd
import os

class CustomExperimenter(Experimenter):
    result_path : str = "results/custom"
    
    def __init__(self, args, **kwargs):
        super().__init__(args, **kwargs)
        self.framework = kwargs["framework"]
        self.name = kwargs.get("name", "")
        self.result_path = f"results/custom_{self.name}"
        self.state = create_initial_state(self.args.task, start_task_id=1, data_config=self.data_config, low_is_better=self.args.low_is_better, name="")
    
    async def run_experiment(self):
        user_requirement = self.state["requirement"]
        preds = await self.framework.run(user_requirement)
        test_preds = preds["test_preds"]
        dev_preds = preds["dev_preds"]
        score_dict = {
            "dev_score": self.evaluate_predictions(dev_preds, "dev"),
            "test_score": self.evaluate_predictions(test_preds, "test")
        }
        results = {
            "score_dict": score_dict,
            "user_requirement": user_requirement,
            "args": vars(self.args)
        }
        self.save_result(results)

    def evaluate_predictions(self, preds, split):
        metric = self.state["dataset_config"]["metric"]
        gt_path = os.path.join(self.state["datasets_dir"][f"{split}_target"])
        gt = pd.read_csv(gt_path)["target"]
        score = evaluate_score(preds, gt, metric)
        return score        
    

    def load_datasets(self):
        train_path = self.state["datasets_dir"]["train"]
        dev_path = self.state["datasets_dir"]["dev"]
        test_path = self.state["datasets_dir"]["test"]
        train = pd.read_csv(train_path)
        dev = pd.read_csv(dev_path)
        test = pd.read_csv(test_path)
        return train, dev, test
    

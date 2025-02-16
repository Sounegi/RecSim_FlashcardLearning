from datetime import datetime
import numpy as np

def reward(responses):
    reward = 0.0
    for response in responses:
        reward += int(response._recall)
    return reward

def update_metrics(responses, metrics, info):
    # print("responses: ", responses)
    prs = []
    for response in responses:
        prs.append(response['pr'])
    if type(metrics) != list:
        metrics = [prs]
    else:
        metrics.append(prs)
    # print(metrics)
    return metrics

def eval_result(train_time, last_review, history, W):
    with open(f"{datetime.now()}.txt", "w") as f:
        print(train_time, file=f)
        print(last_review, file=f)
        print(history, file=f)
        print(W, file=f)
        # np.einsum('ij,ij->i', a, b)
        last_review = train_time - last_review
        mem_param = np.exp(np.einsum('ij,ij->i', history, W))
        pr = np.exp(-last_review / mem_param)
        print(pr, file=f)
        print(pr)
        print("score:", np.sum(pr) / pr.shape[0], file=f)
        print("score:", np.sum(pr) / pr.shape[0])
from recsim import user
from recsim.choice_model import MultinomialLogitChoiceModel
from .UserState import UserState
from .UserSampler import UserSampler
from .UserResponse import UserResponse
from util import eval_result
import numpy as np

class FlashcardUserModel(user.AbstractUserModel):
  def __init__(self, num_candidates, time_budget, slate_size, seed=0):
    super(FlashcardUserModel, self).__init__(
        UserResponse, UserSampler(
            UserState, num_candidates, time_budget, 
            seed=seed
        ), slate_size)
    self.choice_model = MultinomialLogitChoiceModel({})

  def is_terminal(self):
    terminated = self._user_state._time > self._user_state._time_budget
    if terminated: # run evaluation process
      eval_result(self._user_state._time,
                  self._user_state._last_review.copy(),
                  self._user_state._history.copy(),
                  self._user_state._W.copy())
    return terminated

  def update_state(self, slate_documents, responses):
    for doc, response in zip(slate_documents, responses):
      doc_id = doc._doc_id
      self._user_state._history[doc_id][0] += 1
      if response._recall:
        self._user_state._history[doc_id][1] += 1
      else:
        self._user_state._history[doc_id][2] += 1
      self._user_state._last_review[doc_id] = self._user_state._time
    self._user_state._time += 1

  def simulate_response(self, slate_documents):
    responses = [self._response_model_ctor() for _ in slate_documents]
    # Get click from of choice model.
    self.choice_model.score_documents(
      self._user_state, [doc.create_observation() for doc in slate_documents])
    scores = self.choice_model.scores
    selected_index = self.choice_model.choose_item()
    # Populate clicked item.
    self._generate_response(slate_documents[selected_index],
                            responses[selected_index])
    return responses

  def _generate_response(self, doc, response):
    # W = np.array([1,1,1])
    doc_id = doc._doc_id
    W = self._user_state._W[doc_id]
    if not W.any(): # uninitialzed
      self._user_state._W[doc_id] = W = doc.base_difficulty * np.random.uniform(0.5, 2.0, (1, 3)) # a uniform error for each user
      print(W)
    # use exponential function to simulate whether the user recalls
    last_review = self._user_state._time - self._user_state._last_review[doc_id]
    x = self._user_state._history[doc_id]

    pr = np.exp(-last_review / np.exp(np.dot(W, x))).squeeze()
    print(f"time: {self._user_state._time}, reviewing flashcard {doc_id}, recall rate = {pr}")
    if np.random.rand() < pr: # remembered
      response._recall = True
    response._pr = pr
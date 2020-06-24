# encoding: utf-8
"""
@author: Yuxian Meng
@contact: yuxian_meng@shannonai.com

@version: 1.0
@file: test_corefqa
@time: 2020/6/23 20:37

"""

import torch
from model.corefqa import CorefQA
from data_loader.conll_dataloader import CoNLLDataLoader, CoNLLDataset


# MODEL: CorefQA = CorefQA.from_pretrained("/data/nfsdata2/nlp_application/models/bert/chinese_L-12_H-768_A-12")
MODEL: CorefQA = CorefQA.from_pretrained("/xiaoya/pretrain_ckpt/spanbert_base_cased")


def test_forward_with_fake_data():
    """test forward"""
    input_ids = torch.LongTensor([[200, 200, 200, 300, 300]]).long()  # [num_window, ]
    sentence_map = torch.LongTensor([0, 0, 0, 1, 1])
    input_mask = torch.LongTensor([0, 1, 2, 3, 4])
    span_starts = torch.LongTensor([0])
    span_ends = torch.LongTensor([1])
    cluster_ids = torch.LongTensor([1])
    y = MODEL(doc_idx=None, sentence_map=sentence_map, subtoken_map=None, input_ids=input_ids, input_mask=input_mask,
              gold_mention_span=None, token_type_ids=None, attention_mask=None,
              span_starts=span_starts, span_ends=span_ends, cluster_ids=cluster_ids)
    print(y)


def test_get_candidates_spans():
    sentence_map = torch.Tensor([0, 0, 0, 1, 1]).long()
    starts, ends = MODEL.get_candidate_spans(sentence_map)
    golden_starts = torch.Tensor([0, 0, 0, 1, 1, 2, 3, 3, 4]).long()
    golden_ends = torch.Tensor([0, 1, 2, 1, 2, 2, 3, 4, 4]).long()
    assert (starts == golden_starts).all().item() and (ends == golden_ends).all().item()


def test_get_question_tokens():
    sentence_map = torch.Tensor([0, 0, 0, 1, 1]).long()
    flattened_input_ids = torch.Tensor([0, 1, 2, 3, 4]).long()
    flattened_input_mask = torch.Tensor([0, 1, 2, 3, 4]).long()
    span_start = 0
    span_end = 1
    question_tokens = MODEL.get_question_token_ids(sentence_map=sentence_map,
                                                   flattened_input_ids=flattened_input_ids,
                                                   flattened_input_mask=flattened_input_mask,
                                                   span_start=span_start,
                                                   span_end=span_end)
    golden_question_tokens = torch.Tensor([MODEL.mention_start_idx, 0, 1, MODEL.mention_end_idx, 2]).long()
    assert (golden_question_tokens == question_tokens).all().item()


def test_pad():
    tensors = [torch.LongTensor([1, 2, 3]),
               torch.LongTensor([1, 2]),
               ]
    padded_tensor = CorefQA.pad_stack(tensors, 1)
    golden_tensor = torch.LongTensor(
        [
            [1, 2, 3],
            [1, 2, 1]
        ]
    )
    assert (padded_tensor == golden_tensor).all().item()


def test_forward_with_conll_data():
    """test forward"""

    class Config(object):
        def __init__(self, ):
            self.data_dir = "/xiaoya/data"
            self.sliding_window_size = 128
    config = Config()
    print(config.data_dir)
    dataloader = CoNLLDataLoader(config)
    test_dataloader = dataloader.get_dataloader("test")
    for test_example in test_dataloader:
        print("=*=" * 10)

        y = MODEL(
            doc_idx=test_example["doc_idx"].squeeze(0),
            sentence_map=test_example["sentence_map"].squeeze(0),
            subtoken_map=None,
            input_ids=test_example["flattened_input_ids"].view(-1, config.sliding_window_size),
            input_mask=test_example["flattened_input_mask"].view(-1, config.sliding_window_size),
            gold_mention_span=test_example["mention_span"].squeeze(0),
            token_type_ids=None, attention_mask=None,
            span_starts=test_example["span_start"].squeeze(0),
            span_ends=test_example["span_end"].squeeze(0),
            cluster_ids=test_example["cluster_ids"].squeeze(0),
        )
        print(y)
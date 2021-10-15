from django.forms import model_to_dict


def serialize_qs(qs):
    tmp_lst = [model_to_dict(item) for item in qs]
    tmp_lst.sort(key=lambda x: x["name"])
    return tmp_lst

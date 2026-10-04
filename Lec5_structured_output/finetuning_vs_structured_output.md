Fine-tuning: changes the model's actual weights, permanently

Fine-tuning is a training process. You take a pretrained model and continue training it on additional examples, and gradient descent actually updates the model's internal parameters (the billions of weight values in its layers). After fine-tuning, the model is a genuinely different artifact, saved to disk with new weights, it will behave differently on every future request, forever, regardless of whether you ask for JSON or plain text.

Fine-tuning:  training data → gradient updates → NEW WEIGHTS saved permanently
Constrained decoding (what we've been discussing): changes nothing about the model, only filters its output per-request

Constrained decoding happens entirely at inference time, when you call the API. The model's weights are never touched, never updated, never different afterward. It's the exact same pretrained GPT-5-nano model, completely unmodified, every single time you call it. What changes is a temporary, per-request filter applied to the model's output probabilities, active only for the duration of that one API call, then gone.

Constrained decoding: same frozen weights + grammar mask applied this one time → discarded after the response
# Server Source Code Documentation
## Tora-7b/ToRA-master
- The mathematical reasoning model is developed based on the ToRA project: <https://github.com/microsoft/ToRA>, using the ToRA-7B model. The detailed deployment process can be found in the ToRA project documentation. In this project, the model's reasoning capabilities are primarily used to process and recognize LaTeX code.
- Some scripts in the original ToRA project (ToRA-master) require modifications. The details are as follows:

## tphone
- This module mainly handles server-client communication and invokes image recognition functionality. It includes the basic server module, image recognition invocation module, API interface module, and model invocation module.
- Certain file paths within the folder need to be modified, and some models require purchase or updating the model invocation addresses. The details are as follows:

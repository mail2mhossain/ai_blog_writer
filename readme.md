
conda create -n kindermate python=3.11 -y && conda activate kindermate

conda create --prefix Z:\\conda_env\\ai_blog_writer Python=3.11 -y && conda activate Z:\conda_env\ai_blog_writer

conda activate Z:\conda_env\ai_blog_writer 

### 1. Install PyTorch with CUDA support (for CUDA 12.1)
https://pytorch.org/get-started/locally/
Windows 11:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install git+https://github.com/huggingface/transformers
pip install git+https://github.com/huggingface/accelerate
```
Linux:
```bash
pip install torch torchvision torchaudio
```
### 2. Install bitsandbytes with GPU support:
```bash
pip install bitsandbytes 
```

### 3. Install xformers:
```bash 
pip install xformers --use-pep517

pip install huggingface_hub diffusers transformers accelerate
```

```bash
pip install python-decouple streamlit pytube moviepy imageio gtts pyttsx3
pip install langchain langgraph langchain_openai langchain_community langchain-ollama langchain-experimental
pip install opencv-python
pip install moondream==0.0.5

### 4. Install requirements.txt:
```bash
pip install -r requirements.txt
```

### 5. To remove the environment when done:
```bash
conda remove --name kindermate --all
```

### 6. If you don't have CUDA installed, you'll need to install it first from NVIDIA's website: https://developer.nvidia.com/cuda-12-1-0-download-archive
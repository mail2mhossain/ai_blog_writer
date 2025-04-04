
conda create --prefix Z:\\conda_env\\ai_blog_writer Python=3.11 -y && conda activate Z:\conda_env\ai_blog_writer


### Install requirements.txt:
```bash
pip install -r requirements.txt
```

### To remove the environment when done:
```bash
conda remove --name ai_blog_writer --all
```

### Run the App:
```bash
streamlit run app.py
```
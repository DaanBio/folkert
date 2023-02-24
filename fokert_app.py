import pandas as pd
import openai
import streamlit as st
from stqdm import stqdm
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb





def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def gpt3(prompt_text, max_tokens, temperature, api_key):
    openai.api_key= api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    )
    content = response.choices[0].text.split('.')
    return response.choices[0].text

st.header('Folkerts Chat GPT app')
api_key=st.text_input('API key hier invoeren', type="password")
max_tokens=st.number_input('maximaal aantal gegenereerde woorden', value=200)
temperature=st.number_input('temperatuur waarde (tussen 0 en 1)', min_value=0., max_value=1., value=0.7, step=0.01)
excel_file=st.file_uploader('Upload hier je excel file')

if excel_file:
    df=pd.read_excel(excel_file)

    if st.button("Run ▶"):
        story_list=[]
        for i in stqdm(range(df.shape[0])):
            prompt=df['prompts'][i]
            story_list_temp=gpt3(prompt, max_tokens=max_tokens,temperature=temperature,api_key=api_key)
            story_list.append(story_list_temp)
            

        
        df_answers=pd.DataFrame({'answers':story_list})
        df_final=pd.concat([df,df_answers], axis=1)
        df_xlsx = to_excel(df_final)
        st.success("De omzetting was een succes!")
        st.balloons()
        st.download_button('klik hier om de excel te downloaden', data=df_xlsx, file_name='results.xlsx')

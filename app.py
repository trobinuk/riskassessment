import os
from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/')#,methods=["GET"])

#app.route("/result",methods=["POST","GET"])

def apiTesting():
    #return {"API":"Response Positive and negative"} #http://127.0.0.1:2000
    #return "Hi Robinson!!"
    #def google_results():
    #query = request.args['searchName']
    query = "Adela Williams"
    from googlesearch import search #pip install google
    import requests
    from bs4 import BeautifulSoup #pip install bs4
    import spacy
    nlp = spacy.load("en_core_web_sm")
    import pandas as pd 
    from openpyxl import load_workbook
    import re
    from spacy.matcher import Matcher

    def align_sentence(sent):
        
        sent_split = sent.split()
        result_sent_list = []
        
        for string in sent_split:
            if string.isupper() == True:
                result_sent_list.append(string)
            else:
                y = ''
                for idx,i in enumerate(string):
                    if i.isupper() == True and idx != 0:
                        #print('Inside if',i)
                        i = i.replace(i,' '+i)
                    y = y+i
                result_sent_list.append(y)
            sent_result = ' '.join(result_sent_list)
        return sent_result

    def dob_pattern(text):
        
        doc = nlp(text)
        list_return = []

        pattern_dob_year = [{'LOWER': 'born','POS':'VERB'}, {'POS': 'NUM','LENGTH':4}]
        pattern_dob = [{'LOWER': 'born','POS':'VERB'}, {'POS': 'NUM'},{'POS': 'PROPN'},{'POS': 'NUM'}]              

        matcher = Matcher(nlp.vocab,validate=True)

        matcher.add('Year_of_Birth',[pattern_dob_year])
        matcher.add('Date_of_Birth',[pattern_dob])

        found_matches = matcher(doc)

        if found_matches:
            for match_id,start_pos,end_pos in found_matches:
                string_id = nlp.vocab.strings[match_id]
                span = doc[start_pos:end_pos]
                list_return = [string_id,span.text[5:],start_pos,end_pos]
        else:
            pattern_born = [{'LOWER': 'born','POS':'VERB'}]            
            matcher = Matcher(nlp.vocab,validate=True)
            matcher.add('born',[pattern_born])
            first_match = matcher(doc)

            if first_match:
                pattern_dob1 = [{'POS': 'NUM'},{'POS': 'PROPN'},{'POS': 'NUM','LENGTH':4}]  
                matcher1 = Matcher(nlp.vocab,validate=True)
                matcher1.add('Date_of_Birth1',[pattern_dob1])
                found_matches = matcher1(doc)
                for match_id,start_pos,end_pos in found_matches:
                    string_id = nlp.vocab.strings[match_id]
                    span = doc[start_pos:end_pos]
                    list_return = [string_id,span.text,start_pos,end_pos]

        return list_return

    def address_pattern(text):
        
        doc = nlp(text)
        list_return = []
        pattern_address = [{'LOWER': 'address','POS':'NOUN'}, {'LOWER':'is'},{'POS': 'NUM'},{'TAG':'NNP','OP':'+'},{'IS_PUNCT':True,'OP':'*'},
                        {'POS':'PROPN','OP':'+'},{'IS_PUNCT':True,'OP':'*'},{'POS':'PROPN','OP':'*'},{'POS':'NUM'}]           
        pattern_address1 = [{'POS':'NUM'}, {'POS': 'PROPN','OP':'*'},{'POS': 'NUM'},{'POS': 'PROPN'},{'POS': {"IN": ["NOUN", "PROPN"]}},{'POS': {"IN": ["NOUN", "PROPN"]}},
                        {'IS_PUNCT':True,'OP':'*'},{'POS': 'PROPN'},{'POS':'NUM'}]              

        matcher = Matcher(nlp.vocab,validate=True)

        matcher.add('Address',[pattern_address])
        matcher.add('Address1',[pattern_address1])

        found_matches = matcher(doc)

        for match_id,start_pos,end_pos in found_matches:
            string_id = nlp.vocab.strings[match_id]
            if string_id == 'Address':
                span = doc[start_pos+2:end_pos]
            else:
                span = doc[start_pos:end_pos] 
            list_return = [string_id,span.text,start_pos,end_pos]  

        return list_return

    def find_social_media_acnt(inp_list,line):
        id_name_type = []
        for soc_med_type in inp_list:
            li = list(line.split(' '))
            #print(li)
            for idx,i in enumerate(li):
                if soc_med_type in i and soc_med_type != 'https://www.facebook.com': 
                    id_name_type.append([li[idx+2],soc_med_type])
                    break
                if soc_med_type in i and soc_med_type == 'https://www.facebook.com':
                    if li[idx+2] in ('public','people'):
                        if str(li[idx+4])[-1]:
                            id_name_type.append([li[idx+4]+li[idx+5],soc_med_type])
                        else:
                            id_name_type.append([li[idx+4],soc_med_type])
                        break
                    id_name_type.append([li[idx+2],soc_med_type])
        return id_name_type
        #Match found and then call the append_list function
        
    def append_list(inp_list):
        output_match_term.append(inp_list[0])
        output_word.append(inp_list[1])
        output_line.append(inp_list[2])
        output_list_span_start.append(inp_list[3])
        output_list_span_end.append(inp_list[4]) 
        output_list_search.append(inp_list[5])
        output_list_url_no.append(inp_list[6])
        output_list_line_no.append(inp_list[7]) 
        output_list_match_count.append(inp_list[8])
        
    #search_list = ['Adela williams']#
    #search_list = ['Dan Ricky','Daniel Rickenson','Manideep Bora','Adela williams','Madhu Tejasvi',
    #               'Dustin Alexander','Darrell L Jason','David Nathan','Ricky Pointing','Armond Rashad Morrison']#

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    mod_name = 'Default'

    phone_pattern_1 = '[\d]?[(]{1}[\d]{3}[)]{1}[\s]?[\d]{3}[-\s]{1}[\d]{4}'
    phone_pattern_2 = '[+]{1}[\d]{2}[\s]{1}[(]?[\d]?[)]?[\d]{2}[\s]{1}[\d]{4}[\s]{1}[\d]{4}'
    phone_pattern_3 = '[+]{1}[\d]{2}[\s]{1}[(]?[\d]?[)]?[\d]{3}[\s]{1}[\d]{3}[\s]{1}[\d]{3}'
    phone_pattern_4 = '[\d]{3}[-\s]{1}[\d]{3}[-\s]{1}[\d]{4}'
    phone_pattern = [phone_pattern_1,phone_pattern_2,phone_pattern_3,phone_pattern_4]

    #for query in search_list:
    cnt = 1
    google_result_link = []
    cnt_list = []
    full_name = query.lower()
    name_split = full_name.split()

    output_match_term = []
    output_list_search = []
    output_list_url_no = []
    output_list_line_no = []
    output_list_span_start = []
    output_list_span_end = []
    output_line = []
    output_word = []
    output_list_match_count = []

    entities = []
    labels = []
    model_name = []
    is_correct = []
    position_start = []
    position_end = []
    line_no_list = []
    text_in_the_line = []
    url_no = []

    for url in search(query, tld="com", num=11, stop=11, pause=2):
        #print(str(cnt)+' '+url)
        try:        
            if url[-4:] == '.pdf' or url.find('-image?') != -1:
                raise ValueError('It is a pdf or image file')    
            google_result_link.append(url)
            cnt_list.append(cnt)
            if cnt == 11:
                url = name = query.replace(' ','+')
                url = 'https://www.google.com/search?q='+name

            page = requests.get(url,headers=headers)
            soup = BeautifulSoup(page.text,'html.parser')
            parsed_text = soup.get_text()
            text = parsed_text.split('\n')
            text = list(filter(lambda x: x not in ('','\r'),text))    
            
            data_into_list = []
            try:  
                for line in text:
                    if not line.isspace():
                        if cnt == 11:
                            if line.find('https://') > -1:
                                line = line.replace('https://',' https://')
                        aligned_line = align_sentence(line.strip())
                        splitted_lines_list = re.split('\. |\.\[', aligned_line)
                        for i in splitted_lines_list:
                            data_into_list.append(i)
                line_no = 0
                for line in data_into_list:
                    
                    email_matches = re.finditer('\S+@\S+', line)
                    for m in email_matches:
                        match_count = 0  
                        try:
                            for name in name_split:
                                if m.group(0).lower().find(name) >= 0:
                                    match_count += 1 
                        except:
                            match_count = 0 
                        inp_list = ['Email',m.group(0),line,m.start(),m.end(),query,cnt,line_no,match_count]
                        append_list(inp_list) 
                                        
                    txt_before_and_after = ''
                    for pattern in phone_pattern:
                        for m in re.finditer(pattern,line):
                            match_count = 0
                            try:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                                for name in name_split:
                                    if txt_before_and_after.lower().find(name) >= 0:
                                        match_count += 1 
                            except:
                                match_count = 0
                            inp_list = ['Phone',m.group(0),line,m.start(),m.end(),query,cnt,line_no,match_count]
                            append_list(inp_list) 

                    pattern_values = dob_pattern(line)  
                    if pattern_values:
                        match_count = 0
                        try:
                            if txt_before_and_after is None:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                            
                            for name in name_split:
                                if txt_before_and_after.lower().find(name) >= 0:
                                    match_count += 1
                        except:
                            match_count = 0
                        inp_list = [pattern_values[0],pattern_values[1],line,pattern_values[2],pattern_values[3],query,cnt,line_no,match_count]
                        append_list(inp_list) 

                    pattern_values = address_pattern(line)  
                    if pattern_values:
                        match_count = 0
                        try:
                            if txt_before_and_after is None:
                                if line_no >= 4:
                                    txt_before_and_after = data_into_list[line_no-4]+'\t'+data_into_list[line_no-3]+'\t'+data_into_list[line_no-2]+'\t'+data_into_list[line_no-1]+'\t'+data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                else:
                                    txt_before_and_after = data_into_list[line_no]+'\t'+data_into_list[line_no+1]+'\t'+data_into_list[line_no+2]
                                txt_before_and_after = txt_before_and_after.lower()
                            
                            for name in name_split:
                                if txt_before_and_after.lower().find(name) >= 0:
                                    match_count += 1
                        except:
                            match_count = 0
                        inp_list = [pattern_values[0],pattern_values[1],line,pattern_values[2],pattern_values[3],query,cnt,line_no,match_count]
                        append_list(inp_list) 
                    
                    if cnt == 11:
                        social_media_list = []
                        if line.find('.linkedin.com') > -1:
                            social_media_list.append('.linkedin.com')
                        if line.find('https://www.instagram.com') > -1:
                            social_media_list.append('https://www.instagram.com')
                        if line.find('https://www.facebook.com') > -1:
                            social_media_list.append('https://www.facebook.com')
                        if line.find('twitter.com') > -1:
                            social_media_list.append('twitter.com')
                        #print('social_media_list is ',social_media_list)
                        if social_media_list:
                            out_social_med_list = find_social_media_acnt(social_media_list,line) 
                            #print('out_social_med_list is ',out_social_med_list)
                            match_count = 0  
                            try:
                                for name in name_split:
                                    if out_social_med_list[0][0].lower().find(name) >= 0:
                                        match_count += 1 
                            except:
                                match_count = 0 
                            inp_list = [out_social_med_list[0][1],out_social_med_list[0][0],line,'','',query,cnt,line_no,match_count]
                            append_list(inp_list)                          

                    doc = nlp(str(line.strip()))  

                    mod_name = 'Spacy'
                    for ent in doc.ents:
                        if ent.label_ == 'GPE':
                            is_correct.append('Y')
                            entities.append(str(ent).strip())
                            labels.append(ent.label_)
                            model_name.append(mod_name)
                            position_start.append(ent.start_char)
                            position_end.append(ent.end_char)
                            line_no_list.append(cnt)
                            text_in_the_line.append(line.strip())
                            url_no.append(cnt)

                    line_no += 1
                
            except Exception as e:
                print(e)
                print('Error: '+url)
            cnt += 1
        except ValueError as f:
            print(f)
            print('Error1: '+url)   
            cnt += 1   
        except Exception as e:
            cnt += 1
            print(e)
            print('Error1: '+url)
    
    try:
        df_person_gpe = pd.DataFrame({'Is_correct':is_correct,'Entities':entities,'Labels':labels,'Model_name':model_name,
                                        'Position_start':position_start,'Position_end':position_end,'Line_no':line_no_list,
                                        'Text_in_the_line':text_in_the_line,'URL_No.':url_no})
        df_person_gpe_unique = df_person_gpe[['Entities','URL_No.']]
        df_person_gpe_unique = df_person_gpe_unique.drop_duplicates()
        df_person_gpe_count = df_person_gpe_unique.groupby(['Entities'])['Entities'].count().reset_index(name='count').sort_values(by='count',ascending=False)
        df_person_gpe_max = df_person_gpe_count.query('count == count.max()')

        #output = {'Location':df_person_gpe_max.iloc[0,0]}

        return jsonify({'Location':df_person_gpe_max.iloc[0,0]})

        '''inp_list = ['Location',df_person_gpe_max.iloc[0,0],'','','',query,'','',df_person_gpe_max.iloc[0,1]]
        append_list(inp_list) 

        df = pd.DataFrame({'Match term':output_match_term,'Match Word/Text':output_word,'Line':output_line,
                            'Span start':output_list_span_start,'Span end':output_list_span_end,
                            'output_list_search':output_list_search,'output_list_url_no':output_list_url_no,
                            'output_list_line_no':output_list_line_no,'Match Count':output_list_match_count})

        path = f'{query}_rules_output.xlsx'
        with pd.ExcelWriter(path,engine='xlsxwriter') as writer1:
            df.to_excel(writer1, sheet_name=f'{query}',index=False)

        with pd.ExcelWriter(path,mode='a',engine='openpyxl',if_sheet_exists='replace') as writer:
            df_person_gpe_count.to_excel(writer, sheet_name='GPE_Count',index=False) 

        df1 = pd.DataFrame({'Link_no':cnt_list,'Web Link':google_result_link})
        with pd.ExcelWriter(path,mode='a',engine='openpyxl',if_sheet_exists='replace') as writer:
            df1.to_excel(writer, sheet_name='Web_Links_Google_Search',index=False) '''
    except Exception as e:
            print('Error2: '+url)

if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    #app.run(debug=False)#,port=2000
    app.run()
    

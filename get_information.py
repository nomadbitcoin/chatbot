#!/usr/bin/env python3
# coding: utf-8

'''
    Ha funcoes gerais e selecionadas:

    Funcoes Selecionadas: (comecam com slc_)
        Pega dados do contato selecionado
        * na lista de chat
        * header com nome e "online"
        * dados completos apos clicar em cima do header como legenda status etc

    Funcoes Gerais:
        Pega dados gerais da tela
        * Lista de chats
        * Informacoes de conexao 


    Sempre que for preciso interagir com o navegador ira precisar do driver, senao, ira usar o page source
'''

import bs4
from datetime import datetime

class get_Data():
    """Pega as informacoe"""
    def __init__(self, driver):
        self.driver = driver


    # FUNCOES PEQUENAS PARA NAO PRECISAR REPETIR CODIGO
    def getNow(self):
        '''
            Funcao para retornar tempo e data atual formatado
        '''
        return datetime.now().strftime('%d/%m/%y %H:%M:%S')

    def getPageSource(self, return_content=False):
        self.htmlPage = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')

        if return_content == False:
            return True, 'Atualizado'
        else:
            return self.htmlPage


    # In[6]:


    # VERIFICA SE O WHATSAPP ESTA CONECTADO 
    def verifyConnection(self):
        '''
            Verifica se a div alerta existe e qual o seu conteudo, se for 'Phone not connected' retorna False,
            caso contrario retorna True para conectado.
        '''
        
        self.htmlPage = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        try:
            span_alert = self.htmlPage.find('span',{'class':'_3O0po'})
            text_alert = span_alert.find('div',{'class':'_28Bny'}).text
            if text_alert == 'Phone not connected':
                return False
            else:
                return True
        except Exception as error:
            do = verifyError('self.verifyConnection', error, self.getNow())


    # In[7]:


    def getChats(self):
        '''
            Pega as conversas que estao carregadas no documento atual (posicao do cursos na pagina)
        '''
        self.getPageSource() #atualiza o pagesource em self.htmlPage
        chats = self.htmlPage.find_all('div',{'class':'X7YrQ'})
        return chats


    # In[8]:


    # FUNCOES QUE IRAO PEGAR INFORMACOES DE CADA CHAT
    def getChatName(self, chat):
        '''
            Recebe a div completa de cada chat da lista e ira retornar o "titulo"/ nome da conversa 
            (titulo para caso nao esteja salvo o contato)
        '''
        try:
            contact_name = chat.find('div', {'class':'_3H4MS'}).text
            assert contact_name != '', 'Algum erro ou Sem Nome de Contato'
            return contact_name
        except Exception as error:
            do = verifyError('self.getChatName', error, self.getNow())
            
    def getLabel(self, chat):
        '''
            Recebe um chat e verifica se ha algum label nele, se ha ira retornar o qual label foi encontrado
        
            # TODO: Verificar no banco o que cada label significa para a empresa em questao
        '''
        try:
            label = chat.find('div',{'class':'yKiIK'})
            label = label.find('path').get('fill') if label != None else None
            return label
        except Exception as error:
            do = verifyError('self.getLabel', error, self.getNow())
            pass

    def isGroup(self, chat):
        '''
            Rececebe um chat e verifica se eh um grupo
        
            Quado eh grupo nao tera uma div especifica, entao retornara False
        '''
        try:
            div_contact = chat.find('span',{'class':'_3NWy8'})
            return True if div_contact == None else False
        except Exception as error:
            do = verifyError('isGroup', error, self.getNow())
            pass


    # In[9]:


    # FUNCOES PRA TRATAR O TEMPO E STATUS DAS MENSAGENS, VIA CHAT OU HISTORICO
    def getTime(self, content, chat_or_message):
        '''
            Recebe um chat ou uma mensagem e ira devolver o tempo da mensagem,
            se for um chat ira retornar o horario da ultima mensagem enviada ou recebida,
            se for mensagem ira retornar o time da mensagem
        '''
        # TODO: inserir tratamento de horario para dias da semana e para formatos de horarios diferentes
        try:
            if chat_or_message == 'chat':
                time = content.find('div',{'class':'_0LqQ'}).text
                return time
            elif chat_or_message == 'message':
                time = content.find('span',{'class':'_3fnHB'}).text
                return time
            else:
                return 'content need to be chat or message'
        except Exception as error:
            do = verifyError('getTime', error, self.getNow())
            pass

    def getMsgStatus(self, content, chat_or_message):
        '''
            Recebe uma mensagem de chat ou do historico e retorna seu status,
            se for mensagem enviada ira retornar se foi somente enviada, entregue ou recebida,
            se for recebida ira retornar "received"
        '''
        try:
            if chat_or_message == 'chat':
                status_label = content.find('div',{'class':'_3VIru'})
                return 'Received' if status_label == None else 'Sent'
            elif chat_or_message == 'message':
                return 'need implementation'
        except Exception as error:
            do = verifyError('getMsgStatus', error, self.getNow())
            pass

    def slc_get_name(self):
        '''
            Pega o nome do contato da conversa atual, (header)
        '''
        try:
            name = self.driver.find_element_by_xpath("//div[@class='_19vo_']").text
            return name
        except Exception as error:
            do = verifyError('slc_get_name', error, self.getNow())       
            return 'None'

    def slc_get_messages(self):
        '''
            Pega o historico de mensagens que esta carregada no documento
        '''
        self.getPageSource()
        try:
            messages = self.htmlPage.find_all('div',{'class':'FTBzM'})
            assert messages != [], 'Not Chat Selected'
            return messages
        except Exception as error:
            do = verifyError('slc_get_messages', error, self.getNow())

    def msg_type_content(self, message):
        '''
            Recebe uma mensagem e verifica qual o formato do conteudo: 
                *texto, audio, imagem, video, link, documento, localizacao ou contato
        '''
        try:
            if message.find('span',{'data-icon':'audio-play'}) != None:
                msg_type = 'audio'
            elif message.find('div',{'class':'_1o0MN'}) != None: #testar para outros tipos de documentos
                msg_type = 'document'
            elif message.find('span',{'data-icon':'msg-video-light'}) != None:
                msg_type = 'video'
            elif message.find('div',{'class':'_2kIVZ'}):
                msg_type = 'contact'
            elif message.find('a') != None and 'maps.google' in message.find('a').get('href'):
                msg_type = 'location'
            elif message.find('img',{'class':'_1NZVj'}) != None and 'maps.googleapis' in message.find('img',{'class':'_1NZVj'}).get('src'):
                msg_type = 'live location'
            elif message.find('a') != None:
                msg_type = 'link'
            elif message.find('img') != None and message.find('img').get('alt') != None:
                msg_type = 'emoji'  #se for emoji possui o atributo ~alt~ dentro da tag img
            elif message.find('img') != None:
                msg_type = 'image'
            else:
                msg_type = 'text'
            return msg_type
        except Exception as error:
            do = verifyError('slc_get_name', error, self.getNow())
            return 'Desconhecido'

# FUNCAO DE VERIFICACAO DE ERROS
def verifyError(where, error, when):
    '''
        Verificacao de erros e excecoes 
    '''
    print('Error ocurred in {} at {}: {} {}'.format(where, when, type(error), error))
    pass

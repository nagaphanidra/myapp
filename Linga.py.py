import sys
import random
import sqlite3

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import *

class Boggle_GUI(QMainWindow): # Main window Class

    def __init__(self, dict_filename):
        super().__init__()
        self.setFixedSize(600, 390)
        self.m_dive_panel = []
        self.init_static_data(dict_filename)
        self.init_ui()
        self.cur_dice = []
        self.cur_wordlist = []
        self.exists = False

        self.sqlite_file = "boggle_game.sqlite"
        self.table_name = 'gamestatus'
        self.create_time = 'create_time'
        self.dice_grid_field = 'dice_grid'
        self.word_list_field = 'input_word'

        self.new_game()

    def init_static_data(self, dict_filename): # Manages all the requied data
        
        file_input = open(dict_filename, "r") # Hardcoded file path
        self.words = file_input.read().splitlines() 

        # 16 dice with specified faces
        self.die1 = ('A', 'E', 'A', 'N', 'E', 'G')
        self.die2 = ('A', 'H', 'S', 'P', 'C', 'O')
        self.die3 = ('A', 'S', 'P', 'F', 'F', 'K')
        self.die4 = ('O', 'B', 'J', 'O', 'A', 'B')
        self.die5 = ('I', 'O', 'T', 'M', 'U', 'C')
        self.die6 = ('R', 'Y', 'V', 'D', 'E', 'L')
        self.die7 = ('L', 'R', 'E', 'I', 'X', 'D')
        self.die8 = ('E', 'I', 'U', 'N', 'E', 'S')
        self.die9 = ('W', 'N', 'G', 'E', 'E', 'H')
        self.die10 = ('L', 'N', 'H', 'N', 'R', 'Z')
        self.die11 = ('T', 'S', 'T', 'I', 'Y', 'D')
        self.die12 = ('O', 'W', 'T', 'O', 'A', 'T')
        self.die13 = ('E', 'R', 'T', 'T', 'Y', 'L')
        self.die14 = ('T', 'O', 'E', 'S', 'S', 'I')
        self.die15 = ('T', 'E', 'R', 'W', 'H', 'V')
        self.die16 = ('N', 'U', 'I', 'H', 'M', 'Qu')


        self.dice = [self.die1, self.die2, self.die3, self.die4,self.die5, self.die6, self.die7, self.die8,self.die9, self.die10, self.die11, self.die12,self.die13, self.die14, self.die15, self.die16]

        # self defined static Adjacencies 
        self.die_positions = {0: (1, 4, 5),1: (0, 2, 4, 5, 6),2: (1, 3, 5, 6, 7),3: (2, 6, 7),4: (0, 1, 5, 8, 9), 5: (0, 1, 2, 4, 6, 8, 9, 10),6: (1, 2, 3, 5, 7, 9, 10, 11), 7: (2, 3, 6, 10, 11),8: (4, 5, 9, 12, 13), 9: (4, 5, 6, 8, 10, 12, 13, 14),10: (5, 6, 7, 9, 11, 13, 14, 15),11: (6, 7, 10, 14, 15),12: (8, 9, 13), 13: (8, 9, 10, 12, 14),14: (9, 10, 11, 13, 15),15: (10, 11, 14)}


    def init_ui(self): # components of home window
        self.setWindowTitle("Practise Boggle!")

        dice_panel = QWidget(self)
        self.m_label_list = []

        grid = QGridLayout()
        grid.setSpacing(5)
        for i in range(0, 4):
            for j in range(0, 4):
                tmp_label = QLabel(self)
                tmp_label.setText(str(i * 4 + j))
                tmp_label.setStyleSheet("border: 2px inset red; min-height: 5px;font-size:15px;")
                tmp_label.setAlignment(Qt.AlignCenter)
                self.m_label_list.append(tmp_label)
                grid.addWidget(tmp_label, i, j)

        dice_panel.setLayout(grid)
        dice_panel.setGeometry(54, 60, 300, 240)

        menubar = self.menuBar()
        newFileMenu = menubar.addMenu('PLAY!')
        newFileMenu.setFixedSize(200,160) # Sets on-click menu size
        
        newAct = QAction('Start', self)
        newAct.triggered.connect(self.new_game)
        newFileMenu.addAction(newAct)

        openAct = QAction('Load', self)
        openAct.triggered.connect(self.open_game_menu)

        newFileMenu.addAction(openAct)
        saveAct = QAction('Save', self)
        saveAct.triggered.connect(self.save_game_menu)

        newFileMenu.addAction(saveAct)

        self.m_wordlist_widget = QTextEdit(self)
        self.m_wordlist_widget.setGeometry(384, 72, 136, 216)
        self.m_wordlist_widget.setReadOnly(True)

        self.m_wordinput_widget = QLineEdit(self)
        self.m_wordinput_widget.setGeometry(66, 312, 276, 24)
        self.m_wordinput_widget.setFocus()
        self.m_wordinput_widget.returnPressed.connect(self.add_new_word)

        self.m_score_btn = QPushButton('Score!', self)
        self.m_score_btn.setGeometry(384, 306, 144, 36)
        self.m_score_btn.clicked.connect(self.calc_score)
        self.show()

    # valid english word check
    def is_valid(self, word_input):
        if word_input in self.words:
            return True
        else:
            return False

   
    def is_long_enough(self, word_input):  #  length of the word 
        if len(word_input) >= 3:
            return True
        else:
            return False

 
    def is_not_repeated(self, word_input):    # repetetion of letters
        occurances = []
        occurances = self.gen_occurances(word_input)
        temp = []

        for each in occurances:
            if len(each) == 1:
                if each not in temp:
                    temp.append(each)
            elif len(each) > 1:
                temp.append(each)

        if len(occurances) > len(temp):
            return False
        else:
            return True

    def gen_occurances(self, word_input): 
        flat_dice = self.flaten_list(self.cur_dice)
        letters = list(word_input)
        occurances = []

        for letter in letters:
            letter = letter.upper()
            indices = [[index for y in x] for index, x in enumerate(flat_dice) if x == letter]
            flat_indices = self.flaten_list(indices)
            occurances.append(flat_indices)

        return occurances

    def find_path_existence(self, dict, key_exp, count, word_input):
        if count >= len(word_input) - 2:
            self.exists = True
            return
        if key_exp in list(dict.keys()):
            count = count + 1
            for val in dict[key_exp]:
                self.find_path_existence(dict, val, count, word_input)

    def flaten_list(self, list_to_flaten):
        flatened_list = []
        flatened_list = [each for sublist in list_to_flaten for each in sublist]
        return flatened_list

    def gen_adjacencies(self, wordInput, occurances):
        tracks = []
        flat_tracks = []
        for x in occurances:
            temp = []
            for y in x:
                temp.append(self.die_positions[y])
            tracks.append(temp)
        flat_tracks = self.flaten_list(tracks)
        return flat_tracks

    def gen_mappings(self, adjacencies, occurances):  # Generates occur/adjacencies mappings
        mappings = {}
        mappings = dict(zip(occurances, adjacencies))
        return mappings

    def is_from_letters(self, wordInput):  # validates whether given input is from grid
        target_list = []
        target_list = self.flaten_list(self.cur_dice)
        counter = 0
        for each in wordInput:
            if each.upper() in target_list:
                counter += 1
        if counter == len(wordInput):
            return True
        else:
            return False

    def is_adjacent(self, wordInput):  # validates if each letter is adjacent to one another
        occurances = []
        mappings = {}
        adjacencies = []
        flat_occurances = []

        occurances = self.gen_occurances(wordInput)

        flat_occurances = self.flaten_list(occurances)

        adjacencies = self.gen_adjacencies(wordInput, occurances)

        mappings = self.gen_mappings(adjacencies, flat_occurances)

        path_dict = {}
        temp = []
        i = 0
        while i < len(wordInput) - 1:
            to_look_in = []
            to_look_for = []
            updated_look_in = []
            if (len(updated_look_in) == 0):
                to_look_in = occurances[i]
            else:
                to_look_in = updated_look_in
            to_look_for = occurances[i + 1]
            for unit in to_look_for:
                updated_look_in = []
                temp = []
                for each in to_look_in:
                    value = mappings[each]
                    if unit in value:
                        if i <= len(wordInput) - 2:
                            updated_look_in.append(unit)
                        temp.append(each)
                path_dict[unit] = temp 
            i += 1

        path_dict = dict([(key, value) for key, value in path_dict.items() if len(value) > 0])
        count = 0
        for i in path_dict:
            for j in path_dict[i]:
                self.find_path_existence(path_dict, j, count, wordInput)
                if self.exists:
                    break
            if self.exists:
                break
        # print("path exists is \t"+str(exists))
        if self.exists:
            self.exists = False
            return True
        else:
            return False

    def validate(self, word_input):  # Function which validates all the required checks
        if self.is_from_letters(word_input):
            if self.is_long_enough(word_input):
                if self.is_valid(word_input):
                    if self.is_not_repeated(word_input):
                        if self.is_adjacent(word_input):
                            return True
                        else:
                            return "The word {} is not present in the grid.".format(word_input)
                    else:
                        return "The word {} is repeteted word".format(word_input)
                else:
                    return "The word {} is not a valid word.".format(word_input)
            else:
                return "The word {} is too short.".format(word_input)
        else:
            return "The word {} is not from the grid.".format(word_input)

    def disp_initial_status(self):
        self.m_wordlist_widget.clear()
        self.m_wordinput_widget.clear()
        for i in range(0, 16):
            self.m_label_list[i].setText(str(self.cur_dice[i][0]))
        for word in self.cur_wordlist:
            self.m_wordlist_widget.append(word)

    def new_game(self):

        dice = [[random.choice(y)] for y in self.dice]
        random.shuffle(dice)
        self.cur_wordlist = []
        self.cur_dice = dice
        self.disp_initial_status()
        self.exists = False
        self.create_database()



    def create_database(self):
        conn = sqlite3.connect(self.sqlite_file)
        c = conn.cursor()
        c.execute('Create Table if not EXISTS ' + self.table_name + ' (create_time Text, dice_grid Text, \
                    input_word Text)')
        conn.commit()
        conn.close()

    def open_game_menu(self): # Manages loading a  saved game
        self.exists = False
        
        conn = sqlite3.connect(self.sqlite_file)
        c = conn.cursor()
        c.execute("select " + self.create_time + " from " + self.table_name)
        result = c.fetchall()

        save_game_list = []
        for record in result:
            save_game_list.append(str(record[0]))

        sel_dlg = Select_game_dlg(save_game_list)
        sel_dlg.exec()

        if len(sel_dlg.m_cur_sel) > 0:
            str_sel = "select * from " + self.table_name + " where create_time = '" + sel_dlg.m_cur_sel + '\''
            c.execute(str_sel)
            result = c.fetchone()

            self.cur_dice = []
            self.cur_wordlist = []
            for dice in result[1].split(' '):
                self.cur_dice.append([dice])

            self.cur_wordlist = result[2].split(' ')
            self.disp_initial_status()

        conn.commit()
        conn.close()


    def save_game_menu(self): # Saves game status into sqlite db file
        conn = sqlite3.connect(self.sqlite_file)
        c = conn.cursor()

        datetime = QDateTime.currentDateTime()
        target_list = self.flaten_list(self.cur_dice)

        params = [ ]
        params.append(datetime.toString())
        params.append(' '.join(target_list))
        params.append(' '.join(self.cur_wordlist))

        insert_sql = 'insert into ' + self.table_name + '(' + self.create_time + ',' +  self.dice_grid_field + ',' +\
                     self.word_list_field + ')' + 'values (?,?,?)'
        c.execute(insert_sql, params)
        conn.commit()
        conn.close()

    def calc_score(self): # Validates the word and calculates total score
        result = ""
        wordUsage = []
        eightPlusCounter = 0
        sevenCounter = 0
        sixCounter = 0
        fiveCounter = 0
        threeFourCounter = 0

        for eachInput in self.cur_wordlist:
            length_of_word = 0
            result = self.validate(eachInput)
            length_of_word = len(eachInput)
            if result is not True:
                print(result)
            else:
                if length_of_word >= 8:
                    if eachInput not in wordUsage:
                        eightPlusCounter += 1
                        wordUsage.append(eachInput)
                        print("The word {} is worth 11 points.".format(eachInput))
                    else:
                        print("The word {} has already been used.".format(eachInput))
                elif length_of_word == 7:
                    if eachInput not in wordUsage:
                        sevenCounter += 1
                        wordUsage.append(eachInput)
                        print("The word {} is worth 5 points.".format(eachInput))
                    else:
                        print("The word {} has already been used.".format(eachInput))
                elif length_of_word == 6:
                    if eachInput not in wordUsage:
                        sixCounter += 1
                        wordUsage.append(eachInput)
                        print("The word {} is worth 3 points.".format(eachInput))
                    else:
                        print("The word {} has already been used.".format(eachInput))
                elif length_of_word == 5:
                    if eachInput not in wordUsage:
                        fiveCounter += 1
                        wordUsage.append(eachInput)
                        print("The word {} is worth 2 points.".format(eachInput))
                    else:
                        print("The word {} has already been used.".format(eachInput))
                elif length_of_word == 4 or length_of_word == 3:
                    if eachInput not in wordUsage:
                        threeFourCounter += 1
                        wordUsage.append(eachInput)
                        print("The word {} is worth 1 point.".format(eachInput))
                    else:
                        print("The word {} has already been used.".format(eachInput))

        total_score = eightPlusCounter * 11 + sevenCounter * 5 + sixCounter * 3 + fiveCounter * 2 + threeFourCounter

        score_dialog = QMessageBox(self)
        score_dialog.setWindowTitle('Play Boggle')
        score_dialog.setFixedSize(304,300)
        score_dialog.setText("<p align='center'>Your total score is {} points! Would you like to play again?".format(total_score))
        score_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        score_dialog.setDefaultButton(QMessageBox.Yes)
        
        reply = score_dialog.exec_()
        if reply == QMessageBox.No:
            exit(0)
        elif reply == QMessageBox.Yes:
            self.new_game()

    def add_new_word(self): # adds new word to the QLineEdit
        if len(self.m_wordinput_widget.text().strip()) > 0:
            self.m_wordlist_widget.append(self.m_wordinput_widget.text().lower())
            self.cur_wordlist.append(self.m_wordinput_widget.text().lower())
            self.m_wordinput_widget.setText('')


class Select_game_dlg(QDialog): # Class that takes care of Saved Game window

    def __init__(self, save_game_list):
        super().__init__()
        self.title = "Select saved game"
        self.setGeometry(100, 100, 640, 400)
        self.save_game_list = save_game_list
        self.m_cur_sel = ''
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)


    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()

        self.tableWidget.setRowCount(len(self.save_game_list))
        self.tableWidget.setColumnCount(1)

        idx = 0
        for s_date in self.save_game_list:
            self.tableWidget.setItem(idx, 0, QTableWidgetItem(s_date))
            idx += 1

        self.tableWidget.setHorizontalHeaderLabels(["Saved Games"])

        self.tableWidget.move(0, 0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

        self.tableWidget.setColumnWidth(0, self.tableWidget.geometry().width())

    def on_click(self):
        if len(self.tableWidget.selectedItems()) > 0:
            print(self.tableWidget.selectedItems()[0].text())
            self.m_cur_sel = self.tableWidget.selectedItems()[0].text()
            self.close()

    def on_resize(self, event):
        width = event.size().width()
        self.tableWidget.setColumnWidth(width)



if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()   
    app.aboutToQuit.connect(app.deleteLater)
    home_window = Boggle_GUI("./words.txt")
    app.exec_()

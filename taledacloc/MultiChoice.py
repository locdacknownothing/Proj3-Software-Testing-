import unittest
import time
from Utils import *

class MultiChoiceUtils(Utils):
    def createQuizIfNotExists(self): # if exists just click
        self.driver.get("https://sandbox.moodledemo.net/course/view.php?id=2")
        
        isQuizExist = True
        try:
            self.driver.find_element(By.PARTIAL_LINK_TEXT, "Black-box testing")
        except NoSuchElementException:
            isQuizExist = False

        if isQuizExist:
            print("Quiz exists")
            return
        
        edit_mode = self.driver.find_element(By.CLASS_NAME, "custom-control-input")
        if not edit_mode.is_selected():
            edit_mode.click()

        try:
            wait = WebDriverWait(self.driver, 5)
            wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='modal-dialog']")))

            skip_tour = self.driver.find_element(By.XPATH,"""//button[text()='Skip tour']""")
            skip_tour.click()
        except TimeoutException: pass
        # continue executing the script if the modal is not found

        wait = WebDriverWait(self.driver, 5)
        add_activity = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "activity-add-text")))
        add_activity.click()

        add_quiz = self.driver.get("https://sandbox.moodledemo.net/course/modedit.php?add=quiz&type&course=2&section=0&return=0&sr=0&beforemod=0")
        quiz_name = self.driver.find_element(By.ID, "id_name")
        quiz_name.clear()
        quiz_name.send_keys("Black-box testing")

        save_quiz = self.driver.find_element(By.ID, "id_submitbutton2")
        save_quiz.click()

        print("Create quiz success")
        
    def createMultiChoice(self):
        # self.driver.get("https://sandbox.moodledemo.net/course/view.php?id=2")
        quiz = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Black-box testing")
        quiz.click()

        questions = self.driver.find_element(By.XPATH, """//a[contains(text(), 'Questions')]""")
        questions.click()

        add_question = self.driver.find_element(By.CSS_SELECTOR, "#action-menu-toggle-1")
        add_question.click()

        # wait = WebDriverWait(self.driver, 5)
        # add_question = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#action-menu-toggle-1")))
        # add_question.click()

        new_question = self.driver.find_element(By.ID, "actionmenuaction-1")
        new_question.click()

        multichoice = self.driver.find_element(By.ID, "item_qtype_multichoice")
        multichoice.click()

        add_multichoice = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Add']")
        add_multichoice.click()
        print("Create multichoice success")

        # return self.driver.current_url

    def setNameAndText(self):
        question_name = self.driver.find_element(By.ID, "id_name")
        question_name.send_keys("Introduction")

        self._textToIframe_("id_questiontext_ifr", "What is Black-box testing?")

    def setChoice(self, number, text, grade):
        # choice_text
        if text:
            id = f"id_answer_{number-1}_ifr"
            self._textToIframe_(id, text)

        if grade != 0:
            choice_grade = self.driver.find_element(By.ID, f"id_fraction_{number-1}")  
            grade_select = Select(choice_grade)
            grade_select.select_by_value("{}".format(grade/100))

        print("Set choice {} success".format(number))

    def saveChanges(self):
        save_changes = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Save changes']")
        save_changes.click()
        print("Save success")
    
    def assertSuccess(self):pass

    def isError(self, number, at, error_message):
        """
            Grade set, but the Answer is blank
        """
        error = None
        if at == 0:
            at = "answer"
        else:
            at = "fraction"

        try:
            error = self.driver.find_element(By.ID, f"id_error_{at}_{number-1}")
        except NoSuchElementException:
            return False

        if error.text.find(error_message) != -1:
            return True
        
        return False

class MultiChoiceTestCase(unittest.TestCase, MultiChoiceUtils):
    def setUp(self):
        self.init()
        self.logIn()
        self.createQuizIfNotExists()
        self.createMultiChoice()
        self.setNameAndText()

    def test_001_001(self):
        self.setChoice(1, "Functionalities of software applications are tested WITHOUT having knowledge of internal code structure, implementation details and internal paths", 100)
        self.setChoice(2, "Non-Functionalities of software applications are tested WITHOUT having knowledge of internal code structure, implementation details and internal paths.", 100)
        self.setChoice(3, "Functionalities of software applications are tested WITH having knowledge of internal code structure, implementation details and internal paths.", 100)
        self.setChoice(4, "Non-Functionalities of software applications are tested WITH having knowledge of internal code structure, implementation details and internal paths.", 0)
        self.saveChanges()

        questions_url = "https://sandbox.moodledemo.net/mod/quiz/edit.php"
        curr_url = self.driver.current_url
        expected = curr_url.find(questions_url) == 0
        print(curr_url)
        self.driver.quit()
        assert expected

    def test_001_002(self):
        self.setChoice(1, "Functionalities of software applications are tested WITHOUT having knowledge of internal code structure, implementation details and internal paths", 100)
        self.saveChanges()

        expected = self.isError(2, 0, "This type of question requires at least 2 choices")
        self.driver.quit()
        assert expected

    def test_001_003(self):
        self.setChoice(1, "Functionalities of software applications are tested WITHOUT having knowledge of internal code structure, implementation details and internal paths", 100)
        self.setChoice(2, None, 100)
        self.saveChanges()

        expected = self.isError(2, 1, "Grade set, but the Answer is blank")
        self.driver.quit()
        assert expected
        
unittest.main()
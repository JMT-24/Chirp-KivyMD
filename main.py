from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
Window.size = (350, 600)
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, NoTransition
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import  ImageLeftWidget, OneLineAvatarIconListItem, IconRightWidget, TwoLineAvatarIconListItem
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.fitimage import FitImage
import sqlite3
import re
import datetime

class LoginScreen(Screen):
    pass
class SignUpScreen(Screen):
    pass
class HomeScreen(Screen):
    pass
class MessageScreen(Screen):
    pass
class FriendScreen(Screen):
    pass
class ProfileScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass
class AddFriendScreen(Screen):
    pass
class CreatePostScreen(Screen):
    pass
class CreateMessageScreen(Screen):
    pass
class EditProfileScreen(Screen):
    pass
class MessageLogScreen(Screen):
    pass

class PracticeApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.logged_in_username = None

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "A700"
        self.menu = self.create_menu()
        screen = Builder.load_file('ScreenDesigns.kv')
        screen_manager = self.create_screen_manager()
        self.create_allTables()
        return screen_manager
        
    def create_menu(self):
        menu_list = [
            {"viewclass": "OneLineListItem", "text": "Switch to Dark Mode"},
            {"viewclass": "OneLineListItem", "text": "Settings", "on_release": lambda x = "Settings": self.settings_action()}
        ]
        return MDDropdownMenu(items=menu_list, width_mult=4)

    def create_screen_manager(self):
        screen_manager = ScreenManager()
        screens = [
            LoginScreen(name='loginScreen'), SignUpScreen(name='signUpScreen'),
            HomeScreen(name='homeScreen'), MessageScreen(name='messageScreen'),
            FriendScreen(name='friendScreen'), ProfileScreen(name='profileScreen'),
            SettingsScreen(name="settingsScreen"), AddFriendScreen(name="addFriendScreen"),
            CreatePostScreen(name="createPostScreen"), CreateMessageScreen(name="createMessageScreen"),
            EditProfileScreen(name="editProfileScreen"), MessageLogScreen(name="messageLogScreen")
        ]
        for screen in screens:
            screen_manager.add_widget(screen)
        return screen_manager
    
    def dropdown(self, button):
        self.menu.caller = button
        self.menu.open()

    def create_allTables(self):
        self.create_usertable()
        self.create_profPictable()
        self.create_userFollowtable()
        self.create_userPoststable()
        self.create_messageTable()

    def create_usertable(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users(
                  id INTEGER PRIMARY KEY,
                  fname TEXT,
                  lname TEXT, 
                  uname TEXT,
                  email TEXT,
                  password TEXT
                  )""")
        
        conn.commit()
        conn.close()

    def create_profPictable(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS profpic(
                id INTEGER PRIMARY KEY,
                userid INTEGER,
                profpicNum INTEGER,
                FOREIGN KEY (userid) REFERENCES users(id)
                )""")
        
        conn.commit()
        conn.close()

    def create_userFollowtable(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS follows(
                id INTEGER PRIMARY KEY,
                userAid INTEGER,
                userBid INTEGER,
                FOREIGN KEY (userAid) REFERENCES users(id),
                FOREIGN KEY (userBid) REFERENCES users(id)
                )""")
        
        conn.commit()
        conn.close()

    def create_userPoststable(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS posts(
                id INTEGER PRIMARY KEY,
                poster_userID INTEGER,
                content TEXT,
                date TIMESTAMP,
                FOREIGN KEY (poster_userID) REFERENCES users(id)
                )""")
        
        conn.commit()
        conn.close()

    def create_messageTable(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY,
                senderID INTEGER,
                receiverID INTEGER,
                messageText TEXT,
                date TIMESTAMP,
                FOREIGN KEY (senderID) REFERENCES users(id),
                FOREIGN KEY (receiverID) REFERENCES users(id)
                )""")  
        conn.commit()
        conn.close()

    def popup_error(self, string):
        close_button = MDFlatButton(text="Close", on_release=self.close_dialog)

        self.dialog = MDDialog(
            title="Error!",
            text = string,
            buttons= [close_button]
        )
        self.dialog.open()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def login_validation(self, username, password): 
        error_string = ""    
        if not username:
            error_string = "Please enter Username to Login"
        elif not password:
            error_string = "Please enter Password to Login"
        else:
            result = self.username_password_validation(username, password)
            if result != "Proceed":
                error_string = result 
            else:
                self.logged_in_username = username
                self.home_action() 
        if error_string:
            self.popup_error(error_string)
        
    def username_password_validation(self, uname, password):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE uname = ?", (uname,))
        result1 = c.fetchone()

        if result1 is None:
            conn.close()
            return "User has not been registered yet"
        else:
            c.execute("SELECT password FROM users WHERE uname = ?", (uname,))
            passw = c.fetchone()
            conn.close()
            if passw[0] != password:
                return f"Password is Incorrect"
            else:
                return "Proceed"

    def register_validation(self, fname, lname, uname, email, password, cpassword):
        error_string = ""
        signUp_validate = self.signUp_emptyField_validation(fname, lname, uname, email, password, cpassword)
        if signUp_validate == "Proceed":
            if self.username_email_validation(uname, email):
                error_string = "Username or Email already taken"
            elif not self.validate_email(email):
                error_string = "Please enter a valid email address"
            elif password != cpassword:
                error_string = "Password and Confirm Password is not the same"
            else:
                self.register(fname, lname, uname, email, password)
                print("Register successfull")
        else:
            error_string = signUp_validate       
        if error_string:
            self.popup_error(error_string)  

    def register(self, fname, lname, uname, email, password):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (fname, lname, uname, email, password) VALUES (:fname, :lname, :uname, :email, :password)",
                  {
                      'fname': fname,
                      'lname': lname,
                      'uname': uname,
                      'email': email,
                      'password': password,
                  })
        
        userid = c.lastrowid
        c.execute("INSERT INTO profpic (userid, profpicNum) VALUES (?, 1)", (userid,))

        print("Register successfull")
        conn.commit()
        conn.close()

    def username_email_validation(self, uname, email):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE uname = ?", (uname,))
        result = c.fetchone()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        result2 = c.fetchone()

        if result is None and result2 is None:
            conn.close()
            return False
        else:
            conn.close()
            return True
        
    def signUp_emptyField_validation(self, fname, lname, uname, email, password, cpassword):
        params = {
            "First Name": fname, "Last Name": lname, "Username": uname, "Email": email, "Password": password, "Password again to Confirm" : cpassword
            }
        for key, val in params.items():
            if not val:
                return f"Please enter your {key}"
        return "Proceed"     

    def validate_email(self, email):
        pattern = r'^\S+@(\w+\.)?(\w+\.(com|edu|gov|co|govt)(\.\w+)?)$'
        if re.match(pattern, email):
            return True
        else:
            return False

    def changescreen_to_signupscreen(self):
        screen_manager = self.root
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'signUpScreen'

    def changescreen_to_loginscreen(self):
        screen_manager = self.root
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'loginScreen'
    
    def home_action(self):
        screen_manager = self.root
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'homeScreen'
        self.close_dialog()
        self.display_allPosts()

    def back_home_action(self):
        screen_manager = self.root
        screen_manager.transition = NoTransition()
        screen_manager.current = 'homeScreen'
        self.display_allPosts()

    def message_action(self):
        screen_manager = self.root
        screen_manager.transition = NoTransition()
        screen_manager.current = 'messageScreen'
        self.displayUserMessages()
        
    def friends_action(self):
        screen_manager = self.root
        screen_manager.transition = NoTransition()
        screen_manager.current = 'friendScreen'

    def profile_action(self):
        screen_manager = self.root
        screen_manager.transition = NoTransition()
        screen_manager.current = 'profileScreen'
        self.update_profile_image()
    
    def back_to_profile(self):
        self.back_to_beforeScreen()
        self.update_profile_image()

    def back_to_beforeScreen(self):
        screen_manager = self.root
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'right'
        screen_manager.current = self.beforeScreen

    def settings_action(self):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'settingsScreen'
        self.menu.dismiss()

    def addFriend_action(self):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'addFriendScreen'

    def createPost_action(self):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'createPostScreen'
        self.update_profile_image()

    def createMessage_action(self):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'createMessageScreen'

    def messageLog_action(self, title, image, userID):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'messageLogScreen'
        self.messageLog_Thisfriend(title, image, userID)

    def messageLog_Thisfriend(self, title, image, userID):
        screen = self.root.get_screen('messageLogScreen')
        screen.ids.messageLog_friendName.title = title
        screen.ids.messageLog_friendPic.source = image
        screen.ids.messageLog_friendID.text = f"{userID}"
        self.display_Message_Log(screen, f"{userID}")

    def editProfile_action(self):
        screen_manager = self.root
        self.beforeScreen = screen_manager.current
        screen_manager.transition = SlideTransition()
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'editProfileScreen'

    def get_users_from_database(self):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()
        return users
    
    def add_userAction(self, userBid):
        user_data = self.database_search_byUsername(self.logged_in_username)
        userAid = user_data[0]
        if userAid != userBid:
            conn = sqlite3.connect('practice_db.db')
            c = conn.cursor()
            c.execute("INSERT into follows (userAid, userBid) VALUES (? , ?)", (userAid, userBid,))
            conn.commit()
            conn.close()
            print("Add success!")

    def display_allUsers(self, search_query=None):
        addfriend_screen = self.root.get_screen('addFriendScreen')
        addfriend_screen.ids.user_list.clear_widgets()  # Clear existing users
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()

        if search_query:
            c.execute("SELECT * FROM users WHERE fname LIKE ? OR lname LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            c.execute("SELECT * FROM users")

        users = c.fetchall()
        conn.close()
        current_user = self.database_search_byUsername(self.logged_in_username)

        for user in users:
            if current_user[0] == user[0]:
                continue
            elif self.isFollowed(user[0]):
                continue
            else:
                profpicNum = self.get_profpicNum_from_database(user[0])
                self.friendsList(addfriend_screen, "plus", user, profpicNum)

    def isFollowed(self, userBid):
        userAid = self.database_search_byUsername(self.logged_in_username)[0]
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT userBid FROM follows WHERE userAid = ?", (userAid,))
        result = c.fetchall()
        conn.close()
        all_userBid = [id for sublist in result for id in sublist]
        if userBid in all_userBid:
            return True
        else:
            return False

    def on_search(self, instance, value):
        self.display_allUsers(value.strip())

    def database_search_byUsername(self, username):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE uname = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result

    def get_profpicNum_from_database(self, userid):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT profpicNum FROM profpic WHERE userid = ?", (userid,))
        profpicNum = c.fetchone()[0] 
        conn.close()
        return profpicNum

    def get_profile_pic(self):
        user_data = self.database_search_byUsername(self.logged_in_username)
        if user_data:
            profpicNum = self.get_profpicNum_from_database(user_data[0])
            return f"images/DP{profpicNum}.jpg"
        else:
            return "images/DP1.jpg"

    def display_userFullname(self, screen):
        user_data = self.database_search_byUsername(self.logged_in_username)
        fullname = f"{user_data[1]} {user_data[2]}"
        if screen == "profileScreen":
            profile_screen = self.root.get_screen('profileScreen')
            profile_screen.ids.users_fullname.clear_widgets()  
            profile_screen.ids.users_fullname.text = fullname
        elif screen == "createPostScreen":
            profile_screen = self.root.get_screen('createPostScreen')
            profile_screen.ids.users_fullname.clear_widgets()  
            profile_screen.ids.users_fullname.text = fullname

    def display_userUsername(self):
        profile_screen = self.root.get_screen('profileScreen')
        profile_screen.ids.users_username.clear_widgets()  
        profile_screen.ids.users_username.text = f"({self.logged_in_username})"
    
    def edit_profile_pic(self, dpNum):
        user_data = self.database_search_byUsername(self.logged_in_username)
        if user_data:
            conn = sqlite3.connect('practice_db.db')
            c = conn.cursor()
            c.execute("UPDATE profpic SET profpicNum = ? WHERE userid = ?", (dpNum, user_data[0],))
            conn.commit()
            conn.close()
            self.popup_sucess("Profile Picture")
        else:
            pass

    def posts_card(self, screen, profIMG, postContent, userFullname):
        prof_image = FitImage(
            source = profIMG,
            radius=[60, 60, 60, 60]
        )
        profile_image_card = MDCard(
            pos_hint={"center_x": .12, "center_y": 0.83},
            radius=50,
            size_hint=(.15, .22)
        )
        profile_image_card.add_widget(prof_image)

        users_fullname_label = MDLabel(
            text = userFullname,
            id="users_fullname",
            adaptive_size=True,
            theme_text_color="Custom",
            text_color = "white",
            pos_hint={"center_x": .5, "center_y": 0.88}
        )
        posted_date = MDLabel(
            text = "1hr ago",
            id="post_date",
            adaptive_size=True,
            theme_text_color="Custom",
            text_color = "white",
            halign = "left",
            font_style = "Caption",
            pos_hint={"center_x": .5, "center_y": 0.75}
        )
        posts_content = MDLabel(
            text = postContent,
            id = "postContent",
            halign = "center",
            size_hint=(None, None), 
            size=(275, 110),  
            pos_hint={"center_x": .5, "center_y": 0.5}
        )
        additional_content_card = MDCard(
            style="filled",
            pos_hint={"center_x": .5, "center_y": .37},
            size_hint=(None, None),
            size=(280, 120),
            theme_bg_color="Custom",
            md_bg_color="white"
        )
        additional_content_card.add_widget(posts_content)

        layout = MDFloatLayout()
        layout.add_widget(profile_image_card)
        layout.add_widget(users_fullname_label)
        layout.add_widget(posted_date)
        layout.add_widget(additional_content_card)

        main_card = MDCard(
            style="filled",
            pos_hint={"center_x": .5},
            size_hint=(None, None),
            size=(300, 200),
            theme_bg_color="Custom",
            md_bg_color="black"
        )
        main_card.add_widget(layout)
        screen.ids.card_items.add_widget(main_card)

    def main_posts(self, screen, profIMG, userID):
        user_data = self.database_search_byUserid(userID)
        fullname = f"{user_data[1]} {user_data[2]}"
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM posts WHERE poster_userID = ?", (user_data[0],))
        posts = c.fetchall()
        conn.close()

        for post in posts:
            postContent = post[2]
            timestamp = post[3]
            self.posts_card(screen, profIMG, postContent, fullname)

    def display_allPosts(self):
        current_user = self.database_search_byUsername(self.logged_in_username)
        home_screen = self.root.get_screen('homeScreen')
        home_screen.ids.card_items.clear_widgets()

        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        c.execute("SELECT * FROM follows WHERE userAid = ?", (current_user[0],))
        friends = c.fetchall()
        conn.close()
        friendsList = [x[2] for x in friends]
        friendsList.append(current_user[0])
        allPostersList = list(set([x[1] for x in posts]))

        for poster in allPostersList:
            if poster in friendsList:
                profpicNum = self.get_profpicNum_from_database(poster)
                image = f"images/DP{profpicNum}.jpg"
                self.main_posts(home_screen, image, poster)
                    

    def update_profile_image(self): 
        profile_screen = self.root.get_screen('profileScreen')
        createPost_screen = self.root.get_screen('createPostScreen')
        profile_image = profile_screen.ids.profile_image
        profile_image2 = createPost_screen.ids.profile_image
        profile_image.source = self.get_profile_pic()
        profile_image2.source = self.get_profile_pic()

        profile_screen.ids.card_items.clear_widgets()
        user_data = self.database_search_byUsername(self.logged_in_username)
        self.main_posts(profile_screen, profile_image.source, user_data[0])

    def popup_sucess(self, string):
        close_button = MDFlatButton(text="Close", on_release=self.close_dialog)

        self.dialog = MDDialog(
            title="Edit Successful!",
            text = "Successfully edited your "+string+"!",
            buttons= [close_button]
        )
        self.dialog.open()

    def popup_editWarning(self, fname, lname, uname, password):
        no_button = MDFlatButton(text="No", on_release = self.close_dialog)
        yes_button = MDFlatButton(text="Yes", on_release = lambda x: self.edit_changes(fname, lname, uname, password))

        self.dialog = MDDialog(
            title="Are you sure?",
            text = "Do you really want to make these changes?",
            buttons= [yes_button, no_button]
        )
        self.dialog.open()

    def edit_changes(self, fname, lname, uname, password):
        user_data = self.database_search_byUsername(self.logged_in_username)
        print(fname, lname, uname, password)
        '''
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        if fname is not None:
            c.execute("UPDATE users SET fname = ? WHERE userid = ?", (fname, user_data[0],))
        if lname is not None:
            c.execute("UPDATE users SET lname = ? WHERE userid = ?", (lname, user_data[0],))
        if uname is not None:
            c.execute("UPDATE users SET uname = ? WHERE userid = ?", (uname, user_data[0],))
        if password is not None:
            c.execute("UPDATE users SET password = ? WHERE userid = ?", (password, user_data[0],))
        conn.commit()
        conn.close()
        '''

    def userFriends(self):
        user_data = self.database_search_byUsername(self.logged_in_username)
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM follows WHERE userAid = ?", (user_data[0],))

        friends = c.fetchall()
        conn.close()
        return friends

    def display_friendsList(self):
        friend_screen = self.root.get_screen('friendScreen')
        friend_screen.ids.user_list.clear_widgets()  # Clear existing users

        friends = self.userFriends()
        for friend in friends:
            user = self.database_search_byUserid(friend[2])
            profpicNum = self.get_profpicNum_from_database(friend[2])
            self.friendsList(friend_screen, "minus", user, profpicNum)

    def friendsList(self, screen, iconName, user, profpicNum):
        image = f"images/DP{profpicNum}.jpg"
    
        if iconName == "minus":
            action = lambda x, userBid=user[0]: self.delete_userAction(userBid)
        elif iconName == "plus":
            action = lambda x, userBid=user[0]: self.add_userAction(userBid)
        screen.ids.user_list.add_widget(
            OneLineAvatarIconListItem(
                ImageLeftWidget(
                    source=image,
                    radius=[60, 60, 60, 60]
                ),
                IconRightWidget(
                    icon = iconName,
                    on_release = action
                ),
                text=f"{user[1]} {user[2]}",
            )
        )

    def displayUserMessages(self):
        message_screen = self.root.get_screen('messageScreen')
        message_screen.ids.message_list.clear_widgets()  # Clear existing users

        friends = self.userFriends()
        for friend in friends:
            user = self.database_search_byUserid(friend[2])
            profpicNum = self.get_profpicNum_from_database(friend[2])
            self.messageFriendsList(message_screen, user, profpicNum)

    def messageFriendsList(self, screen, user, profpicNum):
        image = f"images/DP{profpicNum}.jpg"
        screen.ids.message_list.add_widget(
            TwoLineAvatarIconListItem(
                ImageLeftWidget(
                    source= image,
                    radius=[60, 60, 60, 60]
                ),
                text=f"{user[1]} {user[2]}",
                secondary_text = "Click to send a message",
                on_release = lambda x, userID = user[0], title = f"{user[1]} {user[2]}", sourceimage = image: self.messageLog_action(title, sourceimage, userID)
            )
        )

    def database_search_byUserid(self, userid):
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (userid,))
        result = c.fetchone()
        conn.close()
        return result

    def delete_userAction(self, userBid):
        user_data = self.database_search_byUsername(self.logged_in_username)
        userAid = user_data[0]
        if userAid != userBid:
            conn = sqlite3.connect('practice_db.db')
            c = conn.cursor()
            c.execute("DELETE FROM follows WHERE userAid = ? AND userBid = ?", (userAid, userBid,))
            conn.commit()
            conn.close()
            print("Delete success!")
    
    def create_post(self, content = ""):
        user_data = self.database_search_byUsername(self.logged_in_username)
        current_date = self.get_currentTime()
        if len(content) <= 95:
            conn = sqlite3.connect('practice_db.db')
            c = conn.cursor()
            c.execute("INSERT into posts (poster_userID, content, date) VALUES (?, ?, ?)", (user_data[0], content, current_date,))
            conn.commit()
            conn.close()
            print("Post added to database!")
        else:
            print("Text length exceeded")

    def create_messageLog(self, userID, messageText):
        receiverID = int(userID) 
        #text only accepts str so I made userID str to throw to the messageLog screen, now turn it back into int
        senderID = self.database_search_byUsername(self.logged_in_username)[0]
        current_date = self.get_currentTime()
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("INSERT into messages (senderID, receiverID, messageText, date) VALUES (?, ?, ?, ?)", 
                  (senderID, receiverID, messageText, current_date,))
        conn.commit()
        conn.close()
        print("Message Log added to database!")

    def display_Message_Log(self, screen, receiverID):
        senderID = self.database_search_byUsername(self.logged_in_username)[0]
        home_screen = screen
        home_screen.ids.message_logs.clear_widgets()
        
        conn = sqlite3.connect('practice_db.db')
        c = conn.cursor()
        c.execute("SELECT * FROM messages WHERE (senderID = ? AND receiverID = ?) OR (senderID = ? AND receiverID = ?)", (senderID, receiverID, receiverID, senderID,))
        senderMessages = c.fetchall()
        conn.close()

        for message in senderMessages:
            if message[1] == senderID:
                color = "black"
            else:
                color = "green"
            self.message_card(home_screen, message[3], color)
        
    def message_card(self, screen, messageContent, color):
        posted_date = MDLabel(
            text = "1hr ago",
            id="post_date",
            adaptive_size=True,
            theme_text_color="Custom",
            text_color = "white",
            halign = "left",
            font_style = "Caption",
            pos_hint={"center_x": .5, "center_y": 0.9}
        )
        posts_content = MDLabel(
            text = messageContent,
            id = "postContent",
            halign = "center",
            size_hint=(None, None), 
            size=(275, 110),  
            pos_hint={"center_x": .5, "center_y": 0.5}
        )
        additional_content_card = MDCard(
            style="filled",
            pos_hint={"center_x": .5, "center_y": .43},
            size_hint=(None, None),
            size=(280, 120),
            theme_bg_color="Custom",
            md_bg_color="white"
        )
        additional_content_card.add_widget(posts_content)

        layout = MDFloatLayout()
        layout.add_widget(posted_date)
        layout.add_widget(additional_content_card)

        main_card = MDCard(
            style="filled",
            pos_hint={"center_x": .5},
            size_hint=(None, None),
            size=(300, 160),
            theme_bg_color="Custom",
            md_bg_color = color
        )
        main_card.add_widget(layout)
        screen.ids.message_logs.add_widget(main_card)

    def update_messageLog(self): 
        screen = self.root.get_screen('messageLogScreen')
        receiverID = screen.ids.messageLog_friendID.text
        self.display_Message_Log(screen, receiverID)
        screen.ids.message_content.text = ""

    def get_currentTime(self):
        return datetime.datetime.now()

PracticeApp().run()
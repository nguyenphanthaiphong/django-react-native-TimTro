import React, { useContext, useReducer } from 'react';
import TimTro from './components/TimTro/TimTro';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { IconButton } from 'react-native-paper'; // Adjust import if necessary
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import RegisterScreen from './components/Screen/RegisterScreen';
import LoginScreen from './components/Screen/LoginScreen';
import userReducer from './configs/MyUserReducer';
import MyConText from './configs/MyConText';
import Profile from './components/Profile/Profile';
import LandlordDetails from './components/TimTro/LandlordDetails';


const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const MyStack = () => {
    return (
        <Stack.Navigator>
            <Stack.Screen name="TimTro" component={TimTro} options={{ title: 'Tìm trọ' }} />
            <Stack.Screen name="RegisterScreen" component={RegisterScreen} options={{ title: 'Đăng ký' }} />
            <Stack.Screen name="LoginScreen" component={LoginScreen} options={{ title: 'Đăng nhập' }} />
            <Stack.Screen name="Profile" component={Profile} options={{ title: 'Thông tin người dùng' }} />
            <Stack.Screen name="LandlordDetails" component={LandlordDetails} options={{ title: 'Thông tin chi tiết' }} />

            {/* <Stack.Screen name="Logout" component={LogoutScreen} options={{ title: 'Đăng xuất' }} /> */}
        </Stack.Navigator>
    );
}

const MyTab = () => {
    const [user, dispatch] = useContext(MyConText);
    return (
        <Tab.Navigator>
            
            {user === null ? <>
                <Tab.Screen
                    name="Login"
                    component={LoginScreen}
                    options={{
                        tabBarIcon: () => <IconButton icon="login" size={40} color="green" />
                    }}
                />
                <Tab.Screen
                    name="Register"
                    component={RegisterScreen}
                    options={{
                        tabBarIcon: () => <IconButton icon="account-plus" size={40} color="green" />
                    }}
                />
                
            </> : <>
                    <Tab.Screen
                name="Home"
                component={MyStack}
                options={{
                    tabBarIcon: () => <IconButton icon="home" size={40} color="green" />

                }}/>

                    <Tab.Screen
                name="Profile"
                component={Profile}
                options={{
                    tabBarIcon: () => <IconButton icon="account-circle" size={40} color="green" />

                }}/>
            </>}

        </Tab.Navigator>
    );
}

const App = () => {
    const [user, dispatch] = useReducer(userReducer, null); // Sử dụng null như giá trị mặc định

    return (
        <NavigationContainer>
            <MyConText.Provider value={[user, dispatch]}>
                <MyTab />
            </MyConText.Provider>
        </NavigationContainer>
    );
};

export default App;

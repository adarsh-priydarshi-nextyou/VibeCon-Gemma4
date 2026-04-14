/**
 * Voice Analysis & Intervention System - Mobile App
 * React Native Application with Local ML Processing
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import RecordScreen from './src/screens/RecordScreen';
import InsightsScreen from './src/screens/InsightsScreen';
import InterventionsScreen from './src/screens/InterventionsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Services
import {initializeMLModels} from './src/services/MLService';
import {initializeDatabase} from './src/services/DatabaseService';

const Tab = createBottomTabNavigator();

function App(): React.JSX.Element {
  const [isReady, setIsReady] = React.useState(false);

  React.useEffect(() => {
    // Initialize app on startup
    const initializeApp = async () => {
      try {
        console.log('Initializing database...');
        await initializeDatabase();
        
        console.log('Initializing ML models...');
        await initializeMLModels();
        
        console.log('App initialized successfully');
        setIsReady(true);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setIsReady(true); // Continue anyway
      }
    };

    initializeApp();
  }, []);

  if (!isReady) {
    return null; // Show splash screen
  }

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({route}) => ({
            tabBarIcon: ({focused, color, size}) => {
              let iconName: string;

              switch (route.name) {
                case 'Record':
                  iconName = focused ? 'microphone' : 'microphone-outline';
                  break;
                case 'Insights':
                  iconName = focused ? 'chart-line' : 'chart-line-variant';
                  break;
                case 'Interventions':
                  iconName = focused ? 'headphones' : 'headphones-off';
                  break;
                case 'Settings':
                  iconName = focused ? 'cog' : 'cog-outline';
                  break;
                default:
                  iconName = 'circle';
              }

              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#667eea',
            tabBarInactiveTintColor: '#718096',
            tabBarStyle: {
              backgroundColor: '#ffffff',
              borderTopWidth: 1,
              borderTopColor: '#e2e8f0',
              paddingBottom: 5,
              paddingTop: 5,
              height: 60,
            },
            tabBarLabelStyle: {
              fontSize: 12,
              fontWeight: '600',
            },
            headerStyle: {
              backgroundColor: '#667eea',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}>
          <Tab.Screen
            name="Record"
            component={RecordScreen}
            options={{title: '🎙️ Record'}}
          />
          <Tab.Screen
            name="Insights"
            component={InsightsScreen}
            options={{title: '📊 Insights'}}
          />
          <Tab.Screen
            name="Interventions"
            component={InterventionsScreen}
            options={{title: '🎧 Interventions'}}
          />
          <Tab.Screen
            name="Settings"
            component={SettingsScreen}
            options={{title: '⚙️ Settings'}}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;

import { StyleSheet, SafeAreaView, Platform, StatusBar } from 'react-native';
import { WebView } from 'react-native-webview';

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <WebView 
        source={{ uri: 'https://terra-05l2.onrender.com/' }} 
        style={{ flex: 1 }}
        startInLoadingState={true}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1f2937', // Matches Tailwind gray-800
    // Prevent content from hiding behind the status bar on Android
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
});

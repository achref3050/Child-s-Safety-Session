import SwiftUI
import FirebaseCore
import FirebaseAnalytics
import FirebaseDatabase

// MARK: - Event Model
struct Event: Identifiable, Decodable, Equatable {
    let id = UUID()
    let alert_message: String
    let time_of_detection: String

    static func == (lhs: Event, rhs: Event) -> Bool {
        return lhs.id == rhs.id &&
               lhs.alert_message == rhs.alert_message &&
               lhs.time_of_detection == rhs.time_of_detection
    }
}

// MARK: - Paginated Response
struct PaginatedResponse: Decodable {
    let events: [Event]
    let total_pages: Int
}

// MARK: - ContentView
struct ContentView: View {
    @State private var events: [Event] = []
    @State private var currentPage = 1
    @State private var totalPages = 1
    @State private var errorMessage: String?
    @State private var isDarkMode = false
    @State private var connectionMessage: String = "" // Firebase connection status

    var body: some View {
        NavigationView {
            VStack {
                Text("Parent Notifier")
                    .font(.largeTitle)
                    .padding()

                if let errorMessage = errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding()
                }

                List(events) { event in
                    VStack(alignment: .leading) {
                        Text(event.alert_message)
                            .font(.headline)
                        Text("Detected at: \(event.time_of_detection)")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                }
                .animation(.easeInOut, value: events)

                HStack {
                    Button(action: {
                        if currentPage > 1 {
                            currentPage -= 1
                            fetchEvents()
                        }
                    }) {
                        Text("Previous")
                            .padding()
                            .background(currentPage > 1 ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(currentPage <= 1)

                    Spacer()

                    Text("Page \(currentPage) of \(totalPages)")
                        .font(.subheadline)

                    Spacer()

                    Button(action: {
                        if currentPage < totalPages {
                            currentPage += 1
                            fetchEvents()
                        }
                    }) {
                        Text("Next")
                            .padding()
                            .background(currentPage < totalPages ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(currentPage >= totalPages)
                }
                .padding()

                Button(action: {
                    fetchEvents()
                }) {
                    Text("Check Events")
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.top)

                // Firebase Connection Test Button
                Button(action: {
                    testFirebaseConnection()
                }) {
                    Text("Test Firebase Connection")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.top)

                // Connection Status Message
                Text(connectionMessage)
                    .foregroundColor(.green)
                    .padding(.top)
            }
            .padding()
            .onAppear {
                fetchEvents()
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Toggle(isOn: $isDarkMode) {
                        Text("Dark Mode")
                    }
                    .toggleStyle(SwitchToggleStyle())
                }
            }
            .preferredColorScheme(isDarkMode ? .dark : .light)
        }
    }

    // MARK: - Fetch Events
    func fetchEvents() {
        let ref = Database.database().reference().child("detections")
        
        ref.observeSingleEvent(of: .value) { snapshot in
            guard let value = snapshot.value as? [String: [String: Any]] else {
                DispatchQueue.main.async {
                    errorMessage = "No events found or invalid data format."
                }
                return
            }

            // Parse data
            let loadedEvents: [Event] = value.compactMap { _, eventData in
                guard
                    let alertMessage = eventData["event_message"] as? String,
                    let timeOfDetection = eventData["timestamp"] as? String
                else {
                    return nil
                }
                return Event(alert_message: alertMessage, time_of_detection: timeOfDetection)
            }

            DispatchQueue.main.async {
                self.events = loadedEvents.sorted(by: { $0.time_of_detection > $1.time_of_detection })
                self.totalPages = 1 // Since pagination isn't used, set totalPages to 1
                self.errorMessage = nil
            }
        } withCancel: { error in
            DispatchQueue.main.async {
                errorMessage = "Firebase fetch error: \(error.localizedDescription)"
            }
        }
    }


    // MARK: - Test Firebase Connection
    func testFirebaseConnection() {
        Analytics.logEvent("test_connection", parameters: [
            "name": "Test Event",
            "description": "Testing Firebase Analytics connection."
        ])
        print("Firebase Analytics event logged.")

        let ref = Database.database().reference()
        ref.child("test_connection").setValue("Firebase is connected!") { error, _ in
            if let error = error {
                DispatchQueue.main.async {
                    connectionMessage = "Database error: \(error.localizedDescription)"
                }
                print("Error writing to Firebase Database: \(error.localizedDescription)")
            } else {
                DispatchQueue.main.async {
                    connectionMessage = "Successfully connected to Firebase!"
                }
                print("Firebase Database test successful!")
            }
        }
    }
}
